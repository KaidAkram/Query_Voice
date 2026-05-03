# query_voice_root/agentic_pipeline/graph.py
import os
import re
import json
import torch
import sqlite3
import gc
import pandas as pd
from typing import List, TypedDict, Optional, Any
from datetime import datetime
from difflib import SequenceMatcher
from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from peft import PeftModel
import chromadb
from chromadb.utils import embedding_functions

# Import the existing rewriter node
from nodes.rewriter import intent_rewriter_node

# --- Enterprise Feature: Semantic Cache ---
class SemanticCache:
    """Lightweight in-memory cache. Bypasses Generator if a 95%+ similar
    query was already answered successfully."""
    def __init__(self, threshold=0.95):
        self.threshold = threshold
        self._store = {}  # {intent_string: {"sql": str, "result": dict}}

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def lookup(self, intent: str):
        for cached_intent, payload in self._store.items():
            if self._similarity(intent, cached_intent) >= self.threshold:
                print(f"--- [CACHE HIT] Similarity {self._similarity(intent, cached_intent):.0%} "
                      f"to cached: '{cached_intent[:50]}...' ---")
                return payload
        return None

    def store(self, intent: str, sql: str, result: dict):
        self._store[intent] = {"sql": sql, "result": result}

# Module-level singleton so the cache persists across graph invocations
_semantic_cache = SemanticCache()


# --- Enterprise Feature: Correction Telemetry Logger ---
def _log_correction(user_intent, failed_sql, error_message, successful_sql=None):
    """Appends self-correction events to logs/correction_telemetry.json
    for future model fine-tuning."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "agentic_pipeline", "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_PATH = os.path.join(LOG_DIR, "correction_telemetry.json")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_intent": user_intent,
        "failed_sql": failed_sql,
        "error_message": error_message,
        "successful_sql": successful_sql
    }

    existing = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

# 1. Define the State
class GraphState(TypedDict):
    raw_voice_input: str
    core_intent: str
    inferred_tables: List[str]
    routing_decision: str  # "dictionary", "golden_queries", or "both"
    is_irrelevant: bool    # Guardrail flag
    retrieved_context: str
    generated_sql: str
    error_traceback: Optional[str]
    execution_result: Optional[Any]
    retry_count: int
    final_answer: str      # Natural language summary

# 2. Local Model Loader
def load_local_llm():
    gc.collect()
    torch.cuda.empty_cache()
    
    # 1. Exact path to weights to prevent re-downloading
    LOCAL_MODEL_PATH = "D:/huggingface_cache/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/c03e6d358207e414f1eca0bb1891e29f1db0e242"
    BASE_MODEL = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else "Qwen/Qwen2.5-Coder-7B-Instruct"
    
    ADAPTER_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "ml_experiments", "v3_qlora_model", "checkpoint-376"
    ))
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )
    
    print(f"Loading Local Base Model: {BASE_MODEL}...")
    
    # Force local_files_only to prevent Hub connection attempts
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, local_files_only=True)
    
    # Path for temporary weight offloading
    offload_dir = os.path.join(os.path.dirname(ADAPTER_PATH), "offload_cache")
    if not os.path.exists(offload_dir): os.makedirs(offload_dir)

    # Hard-limit system RAM to force offloading early
    max_memory = {0: "7GiB", "cpu": "4GiB"} 

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        max_memory=max_memory,
        torch_dtype=torch.float16, 
        low_cpu_mem_usage=True,
        offload_folder=offload_dir,
        offload_state_dict=True,
        local_files_only=True
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    pipe = pipeline(
        "text-generation", model=model, tokenizer=tokenizer,
        max_new_tokens=256, temperature=0.1, do_sample=True,
        pad_token_id=tokenizer.eos_token_id, return_full_text=False
    )
    return HuggingFacePipeline(pipeline=pipe)

# 3. Define the Nodes
def router_node(state: GraphState):
    """Semantic Gatekeeper: Decides if query is in-scope or irrelevant."""
    intent = state["core_intent"].lower()
    
    # List of keywords allowed for SQL generation
    keywords = ["user", "product", "sale", "revenue", "profit", "price", "cost", "premium", "country", "category"]
    is_relevant = any(word in intent for word in keywords)
    
    if not is_relevant:
        print(f"--- [ROUTER] Warning: Query is OUT-OF-SCOPE ---")
        return {"is_irrelevant": True, "routing_decision": "none"}
    
    # If relevant, decide context type
    if any(word in intent for word in ["and", "total", "last", "top", "profitable"]):
        decision = "both"
    else:
        decision = "dictionary"
        
    print(f"--- [ROUTER] Query is In-Scope. Decision: {decision} ---")
    return {"is_irrelevant": False, "routing_decision": decision}

def retriever_node(state: GraphState):
    """Fetches context from local ChromaDB."""
    if state.get("is_irrelevant"):
        return {"retrieved_context": "User asked an irrelevant question."}

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data_engineering", "chroma_db_v4")
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
    
    schema_coll = client.get_collection(name="queryvoice_schema", embedding_function=ef)
    golden_coll = client.get_collection(name="queryvoice_golden_queries", embedding_function=ef)
    
    context_parts = []
    # Always fetch scope first for grounding
    scope_results = schema_coll.query(query_texts=["database scope"], n_results=1)
    context_parts.extend(scope_results["documents"][0])

    for table in state["inferred_tables"]:
        results = schema_coll.query(query_texts=[table], n_results=10) # Increased for full schema coverage
        context_parts.extend(results["documents"][0])
    
    # 2. Intent-Driven Schema Search: Specifically find columns/logic matching the user's request
    print(f"--- [RETRIEVER] Performing intent-driven schema search... ---")
    intent_schema = schema_coll.query(query_texts=[state["core_intent"]], n_results=5)
    context_parts.extend(intent_schema["documents"][0])
            
    if state["routing_decision"] in ["golden_queries", "both"]:
        results = golden_coll.query(query_texts=[state["core_intent"]], n_results=2)
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_parts.append(f"Example Question: {doc}\nExample SQL: {meta['sql']}")
            
    return {"retrieved_context": "\n\n".join(context_parts)}

def generator_node(state: GraphState, llm):
    """Generates SQL OR returns a polite Out-of-Scope message."""
    from langchain_core.prompts import PromptTemplate
    
    # 1. Handle Irrelevant Queries
    if state.get("is_irrelevant"):
        response = (
            f"I'm sorry, I don't have information regarding your request ('{state['core_intent']}') in this database. "
            "Currently, I am grounded in your 'SaaS Subscription' data, which includes information on:\n"
            "* Users: Names, countries, and premium status.\n"
            "* Products: Categories (SaaS Subscription, Consulting, etc.), prices, and costs.\n"
            "* Sales: Revenue, profit, and transaction timestamps.\n"
            "Please ask me a question related to these areas!"
        )
        return {"generated_sql": response}

    # 2. Handle SQL Generation
    error_msg = ""
    if state.get("error_traceback"):
        error_msg = (
            f"\n\nCRITICAL: Your previous query failed with this SQLite error: {state['error_traceback']}\n"
            "You must fix the SQL to resolve this exact error. Do not use MySQL/Postgres syntax (like DATE_SUB); "
            "use SQLite date() functions and correct column names."
        )

    template = """<|im_start|>system
You are a Text-to-SQL expert for the QueryVoice system. 
Generate a valid SQLite query based ONLY on the provided context.
Output ONLY the raw SQL code. No markdown, no triple backticks, no explanations.

STRICT RULES:
1. !!! MANDATORY: PROFIT vs REVENUE !!!
   - If the user asks for "PROFIT", "MARGIN", or "EARNINGS", you MUST use the `profit` column.
   - If the user asks for "REVENUE", "SALES", or "TOTAL MADE", you MUST use the `revenue` column.
   - NEVER use `revenue` when `profit` is requested. This is the most common error; avoid it.
2. Use ONLY the tables and columns explicitly listed in the 'Context' below. 
3. Do not guess column names. If you are unsure, look for Business Concept definitions in the context.
4. UNIT PRICE: 'Products costing more than X' refers to the `unit_price` filter in `dim_products`.
{error_info}<|im_end|>
<|im_start|>user
Context:
{context}

Question:
{intent}

Inferred Tables: {tables}<|im_end|>
<|im_start|>assistant
"""
    prompt = PromptTemplate(template=template, input_variables=["context", "intent", "tables", "error_info"])
    chain = prompt | llm
    
    print(f"--- [GENERATOR] Generating SQL (Attempt {state['retry_count'] + 1})... ---")
    sql = chain.invoke({
        "context": state["retrieved_context"],
        "intent": state["core_intent"],
        "tables": ", ".join(state["inferred_tables"]),
        "error_info": error_msg
    })
    
    return {"generated_sql": sql.strip()}

def sql_evaluator_node(state: GraphState):
    """Sandbox execution with Security Guardrails, Auto-Patcher, and Telemetry."""
    if state.get("is_irrelevant") or state["generated_sql"].startswith("I'm sorry"):
        return {"execution_result": None, "error_traceback": None}

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data_engineering", "queryvoice_local.db")
    sql = state["generated_sql"]
    print(f"--- [EVALUATOR] Testing SQL: {sql[:50]}... ---")

    # 1. SQL Security Guardrail (The Shield)
    BLOCKED_PATTERN = re.compile(
        r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\b", re.IGNORECASE
    )
    if BLOCKED_PATTERN.search(sql):
        error_msg = "SECURITY BLOCK: Destructive operations are not allowed."
        print(f"[{error_msg}]")
        _log_correction(state.get("core_intent", ""), sql, error_msg)
        return {"error_traceback": error_msg, "execution_result": None}

    # 2. SQL Auto-Patcher: Deterministic Profit vs Revenue Correction
    original_sql = sql
    user_question = state["raw_voice_input"].lower()
    intent = state.get("core_intent", "").lower()

    if ("profit" in user_question or "profit" in intent) and "revenue" in sql.lower():
        print("--- [AUTO-PATCHER] Correcting LLM Semantic Bias: Swapping 'revenue' for 'profit' ---")
        sql = sql.replace("revenue", "profit").replace("REVENUE", "PROFIT")
        sql = sql.replace("total_revenue", "total_profit")
        _log_correction(state.get("core_intent", ""), original_sql,
                        "AUTO-PATCHER: revenue -> profit swap", successful_sql=sql)

    # 3. Execute SQL in Sandbox
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        print("[SUCCESS]: SQL execution successful.")
        result = df.to_dict()
        # Store in Semantic Cache on success
        _semantic_cache.store(state.get("core_intent", ""), sql, result)
        return {"execution_result": result, "error_traceback": None}
    except Exception as e:
        error_str = str(e)
        print(f"[FAILED]: SQL execution failed: {error_str}")
        _log_correction(state.get("core_intent", ""), sql, error_str)
        return {"error_traceback": error_str, "retry_count": state["retry_count"] + 1}

def summarizer_node(state: GraphState, llm):
    """Converts raw SQL results into a natural language response."""
    # 1. Handle Out-of-Scope
    if state.get("is_irrelevant") or state["generated_sql"].startswith("I'm sorry"):
        return {"final_answer": state["generated_sql"]}

    # 2. Handle Errors
    if state["error_traceback"]:
        return {"final_answer": f"I encountered an error while trying to answer: {state['error_traceback']}"}

    # 3. Summarize Success
    from langchain_core.prompts import PromptTemplate
    
    template = """<|im_start|>system
You are a helpful data assistant. Summarize the following SQL result for the user's question.
Be concise and natural. Use currency symbols where appropriate.<|im_end|>
<|im_start|>user
Question: {intent}
SQL Result: {result}
<|im_end|>
<|im_start|>assistant
"""
    prompt = PromptTemplate(template=template, input_variables=["intent", "result"])
    chain = prompt | llm
    
    print(f"--- [SUMMARIZER] Generating final response... ---")
    
    # Truncate result to prevent OOM on massive tables
    raw_res = str(state.get("execution_result", ""))
    if len(raw_res) > 500:
        raw_res = raw_res[:500] + "... [TRUNCATED]"
        
    summary = chain.invoke({
        "intent": state.get("core_intent", "Unknown intent"),
        "result": raw_res
    })
    
    return {"final_answer": summary.strip()}

def should_retry(state: GraphState):
    if state.get("is_irrelevant") or not state["error_traceback"]:
        return "summarizer"
    if "SECURITY BLOCK" in str(state["error_traceback"]):
        return "summarizer"
    if state["retry_count"] >= 3:
        print("--- [ROUTER] Max retries reached. Stopping. ---")
        return "summarizer"
    print("--- [ROUTER] Retrying Generator... ---")
    return "generator"

# --- Enterprise Feature: Cache-Aware Router Node ---
def cache_node(state: GraphState):
    """Checks the Semantic Cache before hitting the Generator."""
    hit = _semantic_cache.lookup(state.get("core_intent", ""))
    if hit:
        return {
            "generated_sql": hit["sql"],
            "execution_result": hit["result"],
            "error_traceback": None
        }
    return {}  # Cache miss, continue to generator

def should_use_cache(state: GraphState):
    """If the cache node already populated execution_result, skip to summarizer."""
    if state.get("execution_result") is not None:
        return "summarizer"
    return "generator"

# 4. Build the Graph
def create_graph(llm):
    workflow = StateGraph(GraphState)
    workflow.add_node("rewriter", lambda state: intent_rewriter_node(state, llm))
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("cache", cache_node)
    workflow.add_node("generator", lambda state: generator_node(state, llm))
    workflow.add_node("evaluator", sql_evaluator_node)
    workflow.add_node("summarizer", lambda state: summarizer_node(state, llm))

    workflow.add_edge(START, "rewriter")
    workflow.add_edge("rewriter", "router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "cache")
    workflow.add_conditional_edges("cache", should_use_cache)
    workflow.add_edge("generator", "evaluator")
    workflow.add_conditional_edges("evaluator", should_retry)
    workflow.add_edge("summarizer", END)
    return workflow.compile()

if __name__ == "__main__":
    local_llm = load_local_llm()
    app = create_graph(local_llm)
    
    # TEST CASE 1: Valid Query
    inputs_valid = {
        "raw_voice_input": "Show me revenue for 'SaaS Subscription' from last month.",
        "retry_count": 0
    }
    
    # TEST CASE 2: Irrelevant Query
    inputs_invalid = {
        "raw_voice_input": "Hey QueryVoice, what is the weather in Oran right now?",
        "retry_count": 0
    }
    
    for i, payload in enumerate([inputs_valid, inputs_invalid]):
        print(f"\n--- [PASS {i+1}] EXECUTING AGENTIC PIPELINE ---")
        final_state = app.invoke(payload)
        
        print("\n--- [FINAL PIPELINE OUTPUT] ---")
        # Aggregation-Aware Display
        res = final_state.get("execution_result")
        if res:
            df = pd.DataFrame(res)
            if len(df) == 1 and len(df.columns) == 1:
                # Single Value (Sum, Count, etc.)
                val = df.iloc[0, 0]
                print(f"Result Value: {val}")
            else:
                # Table Result
                print(f"Result Table ({len(df)} rows):")
                print(df.head(5))
        
        print(f"\nASSISTANT: {final_state['final_answer']}")
