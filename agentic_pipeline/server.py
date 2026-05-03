import os
import sys
import time
import shutil
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 1. Setup paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR) # query_voice_root
sys.path.append(ROOT_DIR)

# Import our components
# Note: We import Whisper lazily in the endpoint or at startup
from agentic_pipeline.graph import create_graph, load_local_llm
from ml_experiments.evaluation.live_voice_test import get_asr_pipeline

app = FastAPI(title="QueryVoice API", description="Voice-to-SQL Agentic Pipeline")

# 2. CORS Middleware (Crucial for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Global Models
llm = None
agent_app = None
asr_pipeline = None

@app.on_event("startup")
async def startup_event():
    global llm, agent_app, asr_pipeline
    print("\n--- SERVER STARTUP: LOADING MODELS ---")
    
    # Load LLM (Qwen-7B)
    llm = load_local_llm()
    agent_app = create_graph(llm)
    
    # Load Whisper
    asr_pipeline = get_asr_pipeline()
    
    print("--- SERVER READY: ALL MODELS LOADED ---")

@app.post("/api/v1/query/voice")
async def query_voice(audio: UploadFile = File(...)):
    """Receives an audio file, transcribes it, and runs the agentic pipeline."""
    temp_dir = os.path.join(ROOT_DIR, "debug_audio")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, audio.filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        print(f"\n[REQUEST] Voice query received: {audio.filename}")
        
        # 1. Transcribe
        import soundfile as sf
        import numpy as np
        audio_data, samplerate = sf.read(file_path)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
            
        # Normalize volume to boost quiet speech
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val
            
        start_asr = time.time()
        # Pass both audio data and its real sample rate to Whisper
        res = asr_pipeline({"raw": audio_data, "sampling_rate": samplerate})
        transcript = res.get("text", "").strip()
        
        print("\n" + "="*50)
        print(f"🎙️  ASR TRANSCRIPT: '{transcript}'")
        print("="*50)
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")
            
        # 2. Run Agent
        print("⚙️  Running Agentic Pipeline...")
        start_agent = time.time()
        final_state = agent_app.invoke({"raw_voice_input": transcript, "retry_count": 0})
        
        generated_sql = final_state.get("generated_sql")
        final_answer = final_state.get("final_answer")
        
        print(f"💾 GENERATED SQL: {generated_sql}")
        print(f"🤖 ASSISTANT: {final_answer}")
        print("="*50 + "\n")
        
        # Format response to match ApiService expectations
        return {
            "natural_language_query": transcript,
            "generated_sql": generated_sql,
            "results": final_state.get("execution_result"),
            "summary": final_answer,
            "chart_type": "bar", # Default for now
            "latency": f"{time.time() - start_asr:.2f}s"
        }
        
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # We are NOT deleting the file anymore so you can inspect it
        print(f"[DEBUG] Audio saved at: {file_path}")
        pass

@app.post("/api/v1/query/text")
async def query_text(payload: dict):
    """Processes a text-based natural language query."""
    transcript = payload.get("query", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="Empty query")
        
    start_agent = time.time()
    final_state = agent_app.invoke({"raw_voice_input": transcript, "retry_count": 0})
    
    return {
        "natural_language_query": transcript,
        "generated_sql": final_state.get("generated_sql"),
        "results": final_state.get("execution_result"),
        "summary": final_state.get("final_answer"),
        "chart_type": "bar",
        "latency": f"{time.time() - start_agent:.2f}s"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "online", "gpu": torch.cuda.is_available()}

if __name__ == "__main__":
    # Change CWD to ROOT_DIR so graph.py can find relative files (db, chroma, etc.)
    os.chdir(ROOT_DIR)
    uvicorn.run(app, host="0.0.0.0", port=8000)
