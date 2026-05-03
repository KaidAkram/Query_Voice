# QueryVoice 🎤📊

> An end-to-end Voice-Driven Business Intelligence Application

## Overview

QueryVoice is a portfolio-grade project that allows users to query business databases using natural language voice commands. It leverages state-of-the-art ASR (Automatic Speech Recognition) and Text-to-SQL models to convert spoken questions into executable SQL queries, returning visual business intelligence dashboards.

## Architecture

```
User Voice Input
      │
      ▼
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│   Flutter    │────▶│   FastAPI Backend │────▶│ PostgreSQL │
│   Frontend   │◀────│   (LangChain)    │◀────│  Database   │
└─────────────┘     └──────────────────┘     └────────────┘
                           │     ▲
                           ▼     │
                     ┌──────────────┐
                     │   ChromaDB   │
                     │ (Vector DB)  │
                     └──────────────┘
```

## Tech Stack

| Layer              | Technology                        |
|--------------------|-----------------------------------|
| Frontend           | Flutter (Dart)                    |
| Backend API        | FastAPI (Python)                  |
| Database           | PostgreSQL                        |
| Vector Database    | ChromaDB                          |
| Orchestration      | LangChain                         |
| ASR Model          | OpenAI Whisper (Hugging Face)     |
| Text-to-SQL Model  | T5 / LLaMA (Fine-tuned)          |
| ML Framework       | PyTorch                           |
| Containerization   | Docker & Docker Compose           |

## Project Structure

```
/query_voice_root
├── /frontend_flutter       # Flutter mobile application
├── /backend_fastapi        # FastAPI backend with LangChain orchestration
├── /data_engineering       # ETL pipelines and data generation
├── /ml_experiments         # Model training, evaluation & notebooks
├── /infrastructure         # Docker Compose & container configs
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Flutter SDK 3.x+
- Docker & Docker Compose
- PostgreSQL 15+
- CUDA-compatible GPU (recommended for model training)

### 1. Start Infrastructure

```bash
cd infrastructure
docker-compose up -d
```

### 2. Populate Database

```bash
cd data_engineering
python run_etl.py
```

### 3. Launch Backend

```bash
cd backend_fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Run Flutter App

```bash
cd frontend_flutter
flutter pub get
flutter run
```

## License

This project is built for academic and portfolio purposes.

## Author

Built with ❤️ as a portfolio-grade AI/NLP project.
