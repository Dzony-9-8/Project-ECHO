from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import sys
import os

# Ensure ai-orchestrator is in path for imports
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
orchestrator_path = os.path.join(base_path, "ai-orchestrator")
if orchestrator_path not in sys.path:
    sys.path.append(orchestrator_path)

from core.orchestrator import Orchestrator

app = FastAPI(title="Project ECHO API")
orchestrator = Orchestrator()

@app.on_event("startup")
async def startup_event():
    await orchestrator.start_background_services()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    voice: bool = False

@app.post("/chat")
async def chat(req: ChatRequest):
    response = await orchestrator.process(req.message, use_voice=req.voice)
    return {"response": response}

@app.get("/stream")
async def stream_chat(message: str, voice: bool = False, profile: str = "assistant"):
    # Switch profile if provided
    orchestrator.switch_mode(profile)
    
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': f'Orchestrating with {profile} profile...'})}\n\n"
            
            response = await orchestrator.process(message, use_voice=voice, skip_confirmation=True)
            
            if response is None:
                response = "I processed your request but couldn't generate a response. Please try again."
            
            yield f"data: {json.dumps({'type': 'content', 'content': str(response)})}\n\n"
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"--- STREAM ERROR: {error_detail} ---")
            yield f"data: {json.dumps({'type': 'content', 'content': f'Error: {str(e)}'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- NEW ECHO FRONTEND DECOUPLING: UACP AgentManager Pipeline ---

@app.post("/query")
async def query_endpoint(payload: dict):
    """
    Unified streaming access point for the ECHO frontend.
    Yields structured UACP JSON fragments as the swarm processes the objective.
    """
    user_input = payload.get("user_input")
    task_type = payload.get("task_type", "conversation")
    tags = payload.get("tags", [])

    if not user_input:
        async def err_gen():
            yield f"data: {json.dumps({'agent': 'system', 'type': 'error', 'content': 'Empty input'})}\n\n"
        return StreamingResponse(err_gen(), media_type="text/event-stream")

    async def event_generator():
        try:
            from agents.agent_manager import AgentManager
            from swarm.specialists import DevAgent, ResearchAgent
            from agents.critic_agent import CriticAgent
            from tools.echo_tools.memory_adapter import MemoryAdapter
            from intelligence.interface import IntelligenceLayer
            
            # Setup Intelligence Layer and Memory Proxy
            intel = IntelligenceLayer()
            mem_adapter = MemoryAdapter(intel)

            # Properly initialize specialists per their correct signatures
            dev = DevAgent(intel, orchestrator.root_dir, orchestrator.planner_llm)
            res = ResearchAgent(intel, orchestrator.planner_llm, orchestrator.get_embedder())
            cri = CriticAgent(orchestrator.planner_llm)

            manager = AgentManager(dev, res, cri, mem_adapter)

            # Stream multi-agent execution
            async for event in manager.run_stream(user_input):
                yield f"data: {json.dumps(event)}\n\n"
                
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            import traceback
            print(f"--- /query STREAM ERROR: {traceback.format_exc()} ---")
            yield f"data: {json.dumps({'agent': 'system', 'type': 'error', 'content': f'Backend Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# -----------------------------------------------------------------

@app.post("/profile")
async def set_profile(profile: str):
    success = orchestrator.switch_mode(profile)
    return {"success": success, "current_profile": profile}

@app.post("/dev/plan")
async def dev_plan(objective: str):
    # Ensure developer profile is active
    if orchestrator.mode_name != "developer":
        orchestrator.switch_mode("developer")
        
    if hasattr(orchestrator, 'dev_core'):
        plan = orchestrator.dev_core.plan_change(objective)
        return {"plan": plan}
    return {"error": "Developer core not initialized"}

@app.get("/profile")
async def get_profile():
    return {"profile": orchestrator.mode_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
