# /data_engineering/build_rag.py
"""
RAG Knowledge Base Builder
===========================
Downloads the Hugging Face embedding model, converts our Data Dictionary
into dense vectors, and persists them in a local ChromaDB collection.

This script is idempotent — it can be re-run safely at any time.
It will delete the old collection and rebuild from scratch to ensure
the vector store always mirrors the latest data_dictionary.py.
"""

import os
import sys
import time
import chromadb
from chromadb.utils import embedding_functions
import logging
from data_dictionary import SCHEMA_DOCS, GOLDEN_QUERIES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# 1. Initialize Local ChromaDB (Persistent)
# ==========================================
# This creates a folder called 'chroma_db_storage' to save our vectors permanently.
# Unlike an in-memory client, PersistentClient survives process restarts.
db_path = os.path.join(os.path.dirname(__file__), "chroma_db_storage")
client = chromadb.PersistentClient(path=db_path)

# ==========================================
# 2. Load the Embedding Model
# ==========================================
# 'all-MiniLM-L6-v2' is a lightweight, fast, and highly accurate model.
# It maps text to a 384-dimensional dense vector space.
# On first run, this will download ~80MB from Hugging Face.
logging.info("Loading embedding model 'all-MiniLM-L6-v2'... (first run downloads ~80MB)")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# ==========================================
# 3. Create (or Reset) the Vector Collection
# ==========================================
collection_name = "queryvoice_knowledge_base"
try:
    client.delete_collection(name=collection_name)
    logging.info("Deleted old collection to start fresh.")
except Exception:
    pass  # Collection doesn't exist yet — first run

collection = client.create_collection(
    name=collection_name,
    embedding_function=sentence_transformer_ef,
    metadata={"description": "QueryVoice schema docs and golden SQL queries"}
)

def populate_vector_db():
    """Embed all schema docs and golden queries, then store them in ChromaDB."""
    start_time = time.time()

    # Merge both knowledge sources into one batch
    all_docs = SCHEMA_DOCS + GOLDEN_QUERIES

    ids = [doc["id"] for doc in all_docs]
    documents = [doc["content"] for doc in all_docs]
    metadatas = [{"type": doc["type"], **doc["metadata"]} for doc in all_docs]

    logging.info(f"Embedding {len(all_docs)} documents ({len(SCHEMA_DOCS)} schemas + {len(GOLDEN_QUERIES)} golden queries)...")

    # Insert into ChromaDB — this triggers the embedding model
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    elapsed = round(time.time() - start_time, 2)
    logging.info(f"Successfully added {len(all_docs)} embeddings to ChromaDB in {elapsed}s!")

    # --- Quick sanity check: run a test query ---
    logging.info("--- Sanity Check ---")
    test_question = "How much money did premium users spend?"
    results = collection.query(query_texts=[test_question], n_results=2)

    logging.info(f"Test query: \"{test_question}\"")
    for i, doc_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        logging.info(f"  Match {i+1}: {doc_id} (distance: {distance:.4f})")

    logging.info("RAG Knowledge Base is ready!")

if __name__ == "__main__":
    populate_vector_db()
