"""
LangChain Orchestration Service
=================================
Manages the end-to-end pipeline:
  1. Retrieve relevant schema context from ChromaDB (RAG)
  2. Construct a prompt with schema + user query
  3. Call the Text-to-SQL model
  4. Execute the generated SQL against PostgreSQL
  5. Return structured results
"""

import sys
import os
os.environ["HF_HOME"] = "D:/huggingface_cache"
import pandas as pd

# Add the project root to sys.path so we can import from agentic_pipeline
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from agentic_pipeline.graph import create_graph, load_local_llm
from app.services.asr_service import ASRService

class LangChainOrchestrator:
    """Orchestrates the RAG-augmented Text-to-SQL pipeline."""

    def __init__(self):
        print("--- [ORCHESTRATOR] Initializing LangChain Orchestrator ---")
        self.asr_service = ASRService()
        
        # Load local LLM and compile the LangGraph workflow
        print("--- [ORCHESTRATOR] Loading local LLM for LangGraph ---")
        self.local_llm = load_local_llm()
        self.graph = create_graph(self.local_llm)
        print("--- [ORCHESTRATOR] LangGraph compiled and ready. ---")

    async def process_text_query(self, query: str) -> dict:
        """
        Processes a natural language query through the full pipeline.

        Args:
            query: Natural language question (e.g., "What are total sales by region?")

        Returns:
            dict with keys: generated_sql, results, chart_type, summary
        """
        print(f"--- [ORCHESTRATOR] Processing text query: '{query}' ---")
        payload = {
            "raw_voice_input": query,
            "retry_count": 0
        }
        
        final_state = self.graph.invoke(payload)
        
        res = final_state.get("execution_result")
        results_list = []
        if res:
            df = pd.DataFrame(res)
            results_list = df.to_dict(orient="records")
            
        return {
            "natural_language_query": query,
            "generated_sql": final_state.get("generated_sql", ""),
            "results": results_list,
            "chart_type": "bar" if len(results_list) > 1 else None, # Simplified chart logic
            "summary": final_state.get("final_answer", "")
        }

    async def process_voice_query(self, audio_path: str) -> dict:
        """
        Processes a voice query: ASR transcription → text query pipeline.

        Args:
            audio_path: Path to the recorded audio file

        Returns:
            dict with keys: natural_language_query, generated_sql, results, chart_type, summary
        """
        print(f"--- [ORCHESTRATOR] Processing voice query from audio file ---")
        
        # 1. Transcribe audio to text
        transcription = await self.asr_service.transcribe(audio_path)
        
        if not transcription:
             return {
                 "natural_language_query": "",
                 "generated_sql": "",
                 "results": [],
                 "chart_type": None,
                 "summary": "Sorry, I couldn't understand the audio. Please try again."
             }
             
        # 2. Process the transcribed text through the standard pipeline
        return await self.process_text_query(transcription)
