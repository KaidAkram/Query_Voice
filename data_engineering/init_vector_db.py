# query_voice_root/data_engineering/init_vector_db.py
import os
import yaml
import chromadb
from chromadb.utils import embedding_functions

def init_vector_db():
    try:
        print("--- [INITIALIZING VECTOR DB] ---")
        
        # 1. Setup Paths
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        YAML_PATH = os.path.join(BASE_DIR, "data_engineering", "data_dictionary", "schema_description.yaml")
        DB_PATH = os.path.join(BASE_DIR, "data_engineering", "chroma_db_v4")
        
        print(f"Loading YAML from: {YAML_PATH}")
        if not os.path.exists(YAML_PATH):
            print(f"❌ Error: YAML not found at {YAML_PATH}")
            return

        with open(YAML_PATH, "r") as f:
            config = yaml.safe_load(f)
            
        # 3. Initialize ChromaDB
        print(f"Connecting to ChromaDB at: {DB_PATH}...")
        client = chromadb.PersistentClient(path=DB_PATH)
        
        print("Loading BGE-Small Embedding Model (this may take a moment)...")
        # Ensure sentence-transformers is installed
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
        
        # 4. Create/Get Collections
        schema_coll = client.get_or_create_collection(name="queryvoice_schema", embedding_function=ef)
        golden_coll = client.get_or_create_collection(name="queryvoice_golden_queries", embedding_function=ef)
        
        # 5. Ingest Schema
        print(f"Ingesting Schema ({len(config['tables'])} tables found)...")
        for table in config['tables']:
            table_doc = f"Database Table: {table['name']}. Purpose: {table['description']}"
            schema_coll.add(
                documents=[table_doc],
                metadatas=[{"type": "table", "name": table['name']}],
                ids=[f"table_{table['name']}"]
            )
            for col in table['columns']:
                col_doc = f"Column: {col['name']} (Type: {col['type']}) in Table: {table['name']}. Description: {col['description']}"
                schema_coll.add(
                    documents=[col_doc],
                    metadatas=[{"type": "column", "table": table['name'], "name": col['name']}],
                    ids=[f"col_{table['name']}_{col['name']}"]
                )
                
        # 6. Ingest Business Logic
        print(f"Ingesting {len(config['business_definitions'])} Business Logic rules...")
        for concept, logic in config['business_definitions'].items():
            logic_doc = f"Business Concept: {concept.replace('_', ' ')}. SQLite Logic: {logic}"
            schema_coll.add(
                documents=[logic_doc],
                metadatas=[{"type": "business_logic", "key": concept}],
                ids=[f"logic_{concept}"]
            )
            
        # 7. Ingest Golden Queries
        print(f"Ingesting {len(config['sample_queries'])} Golden Queries...")
        for i, item in enumerate(config['sample_queries']):
            golden_coll.add(
                documents=[item['question']],
                metadatas=[{"sql": item['sql'], "index": i}],
                ids=[f"golden_query_{i}"]
            )
            
        print(f"\n[SUCCESS]: Vector Database initialized.")
        print(f"Final Counts -> Schema: {schema_coll.count()}, Golden: {golden_coll.count()}")

    except Exception as e:
        print("\n[CRITICAL ERROR] DURING INGESTION:")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    init_vector_db()
