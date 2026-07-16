from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import os
import json
from src.utils.logger import get_logger
from src.security import limiter, require_api_key

from langchain_core.messages import HumanMessage, SystemMessage
logger = get_logger("ai_route")

router = APIRouter(prefix="/ai", tags=["JARVIS Core"])

class AIQuery(BaseModel):
    query: str
    module: str
    mock_response: str = None

# Simulating Swarm Tools
def trigger_self_healing(component: str) -> str:
    logger.info(f"DevOps Agent initiating self-healing for {component}")
    return f"Success: Module '{component}' has been successfully rebooted."

def deploy_module(module_name: str) -> str:
    logger.info(f"DevOps Agent deploying new instance of: {module_name}")
    return f"Success: Module '{module_name}' has been deployed."

def query_knowledge_base(topic: str) -> str:
    logger.info(f"Data Agent querying Qdrant for: {topic}")
    return f"Information retrieved: {topic} is integrated."

from langchain_ollama import ChatOllama

# Agent LLM Setup (Local Llama 3 via Ollama)
llm = ChatOllama(
    model="llama3",
    temperature=0,
    base_url="http://ollama:11434"
)



@router.post("/query", dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def process_query(request: Request, query: AIQuery):
    logger.info(f"Swarm Triage received query from {query.module}: {query.query}")
    
    # Triage Agent Logic (Real LLM Routing)
    routing_prompt = f"Analyze this request: '{query.query}'. Should it be routed to the 'DevOpsAgent' (for healing, deploying, fixing) or 'DataAgent' (for info/knowledge)? Reply with exactly one word: DEVOPS or DATA."
    
    try:
        triage_msg = llm.invoke(routing_prompt).content.strip().upper()
        
        target_name = "DevOpsAgent" if "DEVOPS" in triage_msg else "DataAgent"
        logger.info(f"Triage Agent routed control to {target_name}")
        
        # Execute specialized agent
        sys_msg = "You are the DevOps Agent of the OASIS Swarm. Answer the user's request." if target_name == "DevOpsAgent" else "You are the Data Agent of the OASIS Swarm. Answer the user's request."
        result = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=query.query)])
        final_answer = result.content
        
        return {"response": f"[{target_name}] {final_answer}"}
    except Exception as e:
        logger.error(f"Local LLM failed: {e}")
        return {"response": f"[System] Error connecting to Local Ollama Llama 3: {str(e)}"}

