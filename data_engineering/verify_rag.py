# /data_engineering/verify_rag.py

import os
import chromadb
from chromadb.utils import embedding_functions

print("\n--- INITIATING RAG VERIFICATION ---\n")

db_path = os.path.join(os.path.dirname(__file__), "chroma_db_storage")
client = chromadb.PersistentClient(path=db_path)

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="queryvoice_knowledge_base", 
    embedding_function=sentence_transformer_ef
)

# --- THE TEST ---
test_question = "How many SaaS subscriptions did we sell last month?"
print(f"USER ASKED: '{test_question}'\n")

# We ask ChromaDB for the Top 3 most mathematically relevant documents 
# (Increased to 3 to ensure we get dim_products, fact_sales, and maybe a golden query)
results = collection.query(
    query_texts=[test_question],
    n_results=3 
)

print("--- RAG SYSTEM RETRIEVED THE FOLLOWING CONTEXT: ---\n")

for i, doc in enumerate(results['documents'][0]):
    metadata = results['metadatas'][0][i]
    print(f"Result {i+1} (Type: {metadata['type']}):")
    print(f"{doc}\n")
    print("-" * 50)

print("\nVERIFICATION CHECKLIST:")
print("[ ] Did it retrieve 'dim_products' (because of SaaS)?")
print("[ ] Did it retrieve 'fact_sales' (because of sold/month)?")
print("[ ] Did it skip 'dim_users' (because demographics aren't needed here)?")
