import asyncio
import os
from dotenv import load_dotenv

# 1. CRITICAL: Clean environment BEFORE any other imports to silence SDK warnings
load_dotenv()
if "GOOGLE_API_KEY" in os.environ:
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    os.environ.pop("GOOGLE_API_KEY", None)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.agents.llm_agent import Agent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from fastapi.middleware.cors import CORSMiddleware
from google.genai.types import Content, Part

app = FastAPI()

# Enable CORS for the frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8501", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load agents
from agents.class_details_agent.agent import root_agent as class_details_agent
from agents.learning_coach_agent.agent import root_agent as learning_coach_agent
from agents.git_tutor_agent.agent import root_agent as git_tutor_agent
from agents.onboarding_tutor.agent import root_agent as onboarding_tutor_agent
from agents.architectural_time_traveler.agent import root_agent as architectural_time_traveler_agent

session_service = InMemorySessionService()

# Create runners
def create_runner(agent, name):
    return Runner(
        agent=agent,
        app_name=name,
        session_service=session_service,
        auto_create_session=True
    )

class_runner = create_runner(class_details_agent, "class_details_app")
learning_coach_runner = create_runner(learning_coach_agent, "learning_coach_app")
git_tutor_runner = create_runner(git_tutor_agent, "git_tutor_app")
onboarding_tutor_runner = create_runner(onboarding_tutor_agent, "onboarding_tutor_app")
architectural_time_traveler_runner = create_runner(architectural_time_traveler_agent, "architectural_time_traveler_app")

# --- Data Models ---
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

async def process_agent_chat(runner, request: ChatRequest):
    try:
        session = await session_service.get_session(
            app_name=runner.app_name,
            user_id=request.user_id,
            session_id=request.session_id
        )
        if session is None:
            await session_service.create_session(
                app_name=runner.app_name,
                user_id=request.user_id,
                session_id=request.session_id
            )

        content_msg = Content(
            role="user",
            parts=[Part(text=request.message)]
        )
        
        events = runner.run_async(
            new_message=content_msg,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        output_text = ""
        async for event in events:
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    # Accessing 'text' via model_dump() is the safest way to avoid SDK getters triggering warnings
                    p_dict = part.model_dump()
                    if p_dict.get("text"):
                        output_text += p_dict["text"]
                    elif p_dict.get("function_call"):
                        # If we see a function call, we log it but don't add to output_text
                        print(f"Agent is calling function: {p_dict['function_call']['name']}")
        
        return {"response": output_text or "I processed your request but didn't generate a text response."}
    except Exception as e:
        print(f"Error in {runner.app_name} chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    return await process_agent_chat(class_runner, request)

@app.post("/learning_coach/chat")
async def learning_coach_chat(request: ChatRequest):
    return await process_agent_chat(learning_coach_runner, request)

@app.post("/git_tutor/chat")
async def git_tutor_chat(request: ChatRequest):
    return await process_agent_chat(git_tutor_runner, request)

@app.post("/onboarding_tutor/chat")
async def onboarding_tutor_chat(request: ChatRequest):
    return await process_agent_chat(onboarding_tutor_runner, request)

@app.post("/architectural_time_traveler/chat")
async def architectural_time_traveler_chat(request: ChatRequest):
    return await process_agent_chat(architectural_time_traveler_runner, request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)