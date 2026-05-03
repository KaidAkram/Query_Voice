# query_voice_root/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ensure the agentic_pipeline folder is in the path to import graph.py
sys.path.append(os.path.join(os.path.dirname(__file__), "agentic_pipeline"))

from graph import create_graph, load_local_llm

app = FastAPI(title="QueryVoice API", description="FastAPI Bridge for Agentic RAG SQL Pipeline")

# Enable CORS for Flutter interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the local model and graph during startup
print("Initializing QueryVoice LLM and Graph...")
llm = load_local_llm()
query_graph = create_graph(llm)
print("Initialization Complete. API is ready.")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    final_answer: str
    generated_sql: str
    data_payload: dict | list | None
    error: str | None

@app.post("/api/query", response_model=QueryResponse)
async def process_query(req: QueryRequest):
    try:
        # Run the LangGraph orchestrator
        final_state = query_graph.invoke({"raw_voice_input": req.query, "retry_count": 0})
        
        # Extract the relevant fields
        answer = final_state.get("final_answer", "No answer generated.")
        sql = final_state.get("generated_sql", "No SQL generated.")
        payload = final_state.get("execution_result", None)
        error = final_state.get("error_traceback", None)
        
        return QueryResponse(
            final_answer=answer,
            generated_sql=sql,
            data_payload=payload,
            error=error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run with: uvicorn api:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
