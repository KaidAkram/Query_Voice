"""
API Router — Query Endpoints
==============================
Handles voice and text query submissions.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from app.services.langchain_orchestrator import LangChainOrchestrator

router = APIRouter(prefix="/query", tags=["Query"])

# Initialize the orchestrator globally so the model is loaded once
print("--- [ROUTER] Starting LangChainOrchestrator Initialization ---")
orchestrator = LangChainOrchestrator()
print("--- [ROUTER] LangChainOrchestrator Initialized ---")


@router.post("/voice")
async def voice_query(audio: UploadFile = File(...)):
    """
    Accepts an audio file, runs ASR (Whisper) to transcribe,
    then converts the transcription to SQL via the Text-to-SQL pipeline.

    Returns:
        - Transcribed text
        - Generated SQL
        - Query execution results
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    # Save the uploaded file temporarily
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        print(f"--- [ROUTER] Received audio file: {temp_audio_path} ---")
        
        # Process the voice query
        result = await orchestrator.process_voice_query(temp_audio_path)
        return result
        
    except Exception as e:
        print(f"--- [ROUTER] Error processing voice query: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup the temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@router.post("/text")
async def text_query(payload: dict):
    """
    Accepts a natural language text query and converts it to SQL
    via the Text-to-SQL pipeline (with RAG context from ChromaDB).

    Expected payload:
        { "query": "What are total sales by region?" }

    Returns:
        - Generated SQL
        - Query execution results
    """
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query string is required.")

    try:
        result = await orchestrator.process_text_query(query)
        return result
    except Exception as e:
        print(f"--- [ROUTER] Error processing text query: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))
