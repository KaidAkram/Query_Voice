# query_voice_root/agentic_pipeline/test_rewriter.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from peft import PeftModel
from langchain_huggingface import HuggingFacePipeline
from nodes.rewriter import intent_rewriter_node

def load_local_qwen():
    """
    Loads the v3 Qwen model and QLoRA adapter into a LangChain-compatible pipeline.
    """
    # 1. Exact path to weights to prevent re-downloading
    LOCAL_MODEL_PATH = "D:/huggingface_cache/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/c03e6d358207e414f1eca0bb1891e29f1db0e242"
    BASE_MODEL = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else "Qwen/Qwen2.5-Coder-7B-Instruct"
    
    # Path to your saved adapter (update if needed)
    ADAPTER_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "ml_experiments", "v3_qlora_model", "checkpoint-376"
    ))
    
    print(f"Loading Local Base Model: {BASE_MODEL}...")
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )
    
    # Force local_files_only to prevent Hub connection attempts
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, local_files_only=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map={"": 0},
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )
    
    print(f"Applying QLoRA Adapter from: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    
    # Wrap in a Transformers Pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.1, # Keep low for logic tasks
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        return_full_text=False # CRITICAL: Don't echo the prompt back
    )
    
    # Wrap in LangChain
    return HuggingFacePipeline(pipeline=pipe)

def test_rewriter():
    # 1. Setup Local LLM
    llm = load_local_qwen()

    # 2. Define the messy input
    messy_input = "Uhm, hey QueryVoice, can you, like, pull up the... wait, no, just show me the total revenue for the computer category last month?"
    
    print(f"\n--- [RAW VOICE INPUT] ---\n{messy_input}\n")

    # 3. Simulate the LangGraph State
    initial_state = {"raw_voice_input": messy_input}

    # 4. Run the Node
    print("Processing Intent using LOCAL Qwen Engine...")
    result = intent_rewriter_node(initial_state, llm)

    # 5. Print Results
    print("\n--- [LOCAL STRUCTURED OUTPUT] ---")
    print(f"Core Intent:     {result['core_intent']}")
    print(f"Inferred Tables: {result['inferred_tables']}")

if __name__ == "__main__":
    test_rewriter()
