# query_voice_root/agentic_pipeline/nodes/rewriter.py
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Define the Structured Output Schema
class VoiceIntent(BaseModel):
    """The cleaned intent and targeted tables for a Text-to-SQL task."""
    core_intent: str = Field(description="The cleaned, professional English version of the user question. Stripped of filler words and corrections.")
    inferred_tables: List[str] = Field(description="A list of tables needed. Strictly limited to: dim_users, dim_products, fact_sales.")

# 2. System Prompt Architecture (Modified for Local Model Schema Injection)
SYSTEM_PROMPT = (
    "You are a Voice-Intent Translation specialist for the QueryVoice system.\n"
    "Your job is to take raw, messy Speech-to-Text (STT) transcripts and extract the final, logical intent.\n\n"
    "CRITICAL RULES:\n"
    "1. IGNORE FILLER: Strip out 'uh', 'um', 'like', 'hey queryvoice', etc.\n"
    "2. HANDLE CORRECTIONS: If a user says 'wait, no', 'actually', or 'scratch that', DISCARD everything before that phrase and focus on the final instruction.\n"
    "3. MAP SLANG: Map phrases like 'what we made' to 'total revenue' and 'people' to 'users'.\n"
    "4. TABLE LIMIT: Only infer from these 3 tables: [dim_users, dim_products, fact_sales].\n\n"
    "Output MUST be a single, valid JSON object."
)

def intent_rewriter_node(state: dict, llm):
    """
    LangGraph Node: Processes the raw voice input into a structured Intent object.
    Uses PromptTemplate with strict ChatML formatting for local model stability.
    """
    from langchain_core.prompts import PromptTemplate
    raw_input = state.get("raw_voice_input", "")
    
    # Initialize the Parser
    parser = JsonOutputParser(pydantic_object=VoiceIntent)
    
    template = """<|im_start|>system
{system_prompt}
{format_instructions}<|im_end|>
<|im_start|>user
{input}<|im_end|>
<|im_start|>assistant
"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["system_prompt", "input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Local-compatible chain: Prompt | LLM | Parser
    chain = prompt | llm | parser
    
    # Execute
    print(f"Submitting to Local Qwen Model...")
    result = chain.invoke({"system_prompt": SYSTEM_PROMPT, "input": raw_input})
    
    # Update State
    return {
        "core_intent": result.get("core_intent"),
        "inferred_tables": result.get("inferred_tables")
    }
