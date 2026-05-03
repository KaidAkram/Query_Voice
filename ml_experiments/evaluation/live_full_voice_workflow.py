import os
import sys
import torch
import time
import pandas as pd

# 1. Setup paths to allow importing from sibling directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR)) # query_voice_root
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "agentic_pipeline"))

# 2. Import components (Delaying Whisper heavy import)
from live_voice_test import record_audio, test_whisper_transcription
from agentic_pipeline.graph import create_graph, load_local_llm

def run_full_workflow():
    print("\n" + "="*60)
    print("      QUERYVOICE: FULL VOICE-TO-RESULT WORKFLOW")
    print("="*60)
    
    # --- PHASE 1: Initialization ---
    print("\n[STEP 1/4] Initializing Agentic Pipeline (LLM)...")
    # Load LLM first while RAM is fresh
    llm = load_local_llm()
    app = create_graph(llm)
    print("[SUCCESS] Agent Graph Ready.")

    print("\n[STEP 1.5/4] Initializing Whisper (ASR)...")
    # Lazy-load Whisper after LLM is ready
    from live_voice_test import get_asr_pipeline
    asr_pipeline = get_asr_pipeline()
    print("[SUCCESS] Whisper Ready.")

    # --- PHASE 2: Voice Capture ---
    print("\n[STEP 2/4] Voice Capture")
    try:
        # Record for 7 seconds
        audio_file = record_audio(duration=7)
    except Exception as e:
        print(f"[ERROR] Microphone access failed: {e}")
        return

    # --- PHASE 3: Transcription (ASR) ---
    print("\n[STEP 3/4] Transcribing Audio...")
    import soundfile as sf
    audio_data, samplerate = sf.read(audio_file)
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    start_asr = time.time()
    asr_result = asr_pipeline(audio_data)
    transcript = asr_result.get("text", "").strip()
    end_asr = time.time()
    
    if not transcript:
        print("[ERROR] No speech detected.")
        return
        
    print(f"TRANSCRIPTION: '{transcript}'")
    print(f"Time taken (ASR): {end_asr - start_asr:.2f}s")

    # --- PHASE 4: Agentic Pipeline Execution ---
    print("\n[STEP 4/4] Executing Agentic Pipeline...")
    start_agent = time.time()
    
    # The graph expects 'raw_voice_input' and 'retry_count'
    inputs = {
        "raw_voice_input": transcript,
        "retry_count": 0
    }
    
    final_state = app.invoke(inputs)
    end_agent = time.time()

    # --- FINAL OUTPUT DISPLAY ---
    print("\n" + "*"*60)
    print("             FINAL SYSTEM RESPONSE")
    print("*"*60)
    
    # Display SQL if available
    generated_sql = final_state.get("generated_sql", "N/A")
    print(f"\n[INTERNAL] GENERATED SQL:\n{generated_sql}")

    # Display Results Table
    res = final_state.get("execution_result")
    if res:
        df = pd.DataFrame(res)
        print(f"\n[DATABASE] RESULTS ({len(df)} rows):")
        # Display nicely formatted table
        print(df.to_string(index=False))
    
    # Display Natural Language Answer
    print(f"\n[ASSISTANT]: {final_state.get('final_answer', 'No answer generated.')}")
    
    print("\n" + "-"*60)
    print(f"Total Workflow Time: {end_agent - start_asr:.2f}s")
    print("="*60)

if __name__ == "__main__":
    # Ensure we are in the correct directory for relative paths in graph.py
    os.chdir(ROOT_DIR)
    try:
        run_full_workflow()
    except KeyboardInterrupt:
        print("\n[INFO] Workflow cancelled by user.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
