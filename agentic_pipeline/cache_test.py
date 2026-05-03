# query_voice_root/agentic_pipeline/cache_test.py
from graph import create_graph, load_local_llm
import time

def test_cache():
    print("--- [INITIALIZING CACHE TEST] ---")
    llm = load_local_llm()
    app = create_graph(llm)

    query = "What is the total revenue for Consulting Hours?"

    print("\n--- [RUN 1: CACHE MISS] ---")
    start = time.time()
    res1 = app.invoke({"raw_voice_input": query, "retry_count": 0})
    print(f"Time Taken: {time.time() - start:.2f}s")
    print(f"Answer: {res1['final_answer']}")

    print("\n--- [RUN 2: CACHE HIT] ---")
    start = time.time()
    res2 = app.invoke({"raw_voice_input": query, "retry_count": 0})
    print(f"Time Taken: {time.time() - start:.2f}s")
    print(f"Answer: {res2['final_answer']}")

if __name__ == "__main__":
    test_cache()
