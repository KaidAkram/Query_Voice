"""
API Router — Query Endpoints
==============================
Handles voice and text query submissions.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/query", tags=["Query"])


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
    # TODO: Implement ASR → Text-to-SQL → Execute pipeline
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    return {
        "natural_language_query": "placeholder transcription",
        "generated_sql": "SELECT 1;",
        "results": [],
        "chart_type": None,
        "summary": "Placeholder response",
    }


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

    # TODO: Implement LangChain orchestration pipeline
    return {
        "natural_language_query": query,
        "generated_sql": "SELECT 1;",
        "results": [],
        "chart_type": None,
        "summary": "Placeholder response",
    }
