import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.agents.llm_agent import Agent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv

import os

load_dotenv()
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Enable CORS for the Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from agents.class_details_agent.agent import root_agent as class_details_agent
from agents.learning_coach_agent.agent import root_agent as learning_coach_agent
from agents.git_tutor_agent.agent import root_agent as git_tutor_agent

session_service = InMemorySessionService()
runner = Runner(
    agent=class_details_agent,
    app_name="class_details_app",
    session_service=session_service,
    auto_create_session=True
)

learning_coach_runner = Runner(
    agent=learning_coach_agent,
    app_name="learning_coach_app",
    session_service=session_service,
    auto_create_session=True
)

git_tutor_runner = Runner(
    agent=git_tutor_agent,
    app_name="git_tutor_app",
    session_service=session_service,
    auto_create_session=True
)

# --- Data Models ---
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

from google.genai.types import Content, Part

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Ensure the session exists in the backend
        session = await session_service.get_session(
            app_name="class_details_app",
            user_id=request.user_id,
            session_id=request.session_id
        )
        if session is None:
            await session_service.create_session(
                app_name="class_details_app",
                user_id=request.user_id,
                session_id=request.session_id
            )

        # Execute the agent asynchronously
        # We need to send a Content object
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
        # iterate asynchronously (async for)
        async for event in events:
            # ADK events return a Content object
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        output_text += part.text
        
        return {"response": output_text or "Could not generate a response."}
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning_coach/chat")
async def learning_coach_chat(request: ChatRequest):
    try:
        # Ensure session exists in the backend for learning coach
        session = await session_service.get_session(
            app_name="learning_coach_app",
            user_id=request.user_id,
            session_id=request.session_id
        )
        if session is None:
            await session_service.create_session(
                app_name="learning_coach_app",
                user_id=request.user_id,
                session_id=request.session_id
            )

        # Execute agent asynchronously
        content_msg = Content(
            role="user",
            parts=[Part(text=request.message)]
        )
        
        events = learning_coach_runner.run_async(
            new_message=content_msg,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        output_text = ""
        async for event in events:
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        output_text += part.text
        
        return {"response": output_text or "No response found."}
    except Exception as e:
        print(f"Error in learning_coach_chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/git_tutor/chat")
async def git_tutor_chat(request: ChatRequest):
    try:
        session = await session_service.get_session(
            app_name="git_tutor_app",
            user_id=request.user_id,
            session_id=request.session_id
        )
        if session is None:
            await session_service.create_session(
                app_name="git_tutor_app",
                user_id=request.user_id,
                session_id=request.session_id
            )

        content_msg = Content(
            role="user",
            parts=[Part(text=request.message)]
        )
        
        events = git_tutor_runner.run_async(
            new_message=content_msg,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        output_text = ""
        async for event in events:
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        output_text += part.text
        
        return {"response": output_text or "No response found."}
    except Exception as e:
        print(f"Error in git_tutor_chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)