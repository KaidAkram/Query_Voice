"""
QueryVoice — FastAPI Backend
=============================
Main application instance and API router registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import query_router

app = FastAPI(
    title="QueryVoice API",
    description="Voice-driven Business Intelligence backend — ASR, Text-to-SQL, and RAG orchestration.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow Flutter frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "QueryVoice API is running."}


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}


# Register routers
app.include_router(query_router.router, prefix="/api/v1")
