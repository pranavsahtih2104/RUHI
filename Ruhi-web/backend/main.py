
import logging
import sys
from pathlib import Path

# Add project root to sys.path to enable clean imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import settings
from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
    HealthResponse,
)
from backend.services.llm.gemini_service import GeminiService
from backend.services.memory.session_memory import memory_manager
from backend.services.tools.registry import tool_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ruhi.api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="RUHI AI Backend Service — Personal AI Engine",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Service
llm_service = GeminiService()


@app.get("/")
async def root_endpoint():
    """Root endpoint providing links to the UI, API documentation, and health status."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "frontend_url": "http://localhost:5173",
        "api_docs_url": "http://127.0.0.1:8000/docs",
        "health_check_url": "http://127.0.0.1:8000/api/health",
        "message": "RUHI AI Backend Service is active. Visit http://localhost:5173 for the web interface."
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify backend status, active model, and session load."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        llm_provider=llm_service.get_provider_name(),
        model=llm_service.get_model_name(),
        active_sessions=memory_manager.active_session_count(),
        configured_api_key=bool(settings.GEMINI_API_KEY.strip())
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Main conversational endpoint for RUHI Web.
    Maintains session history and queries the underlying LLM provider.
    """
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    session = memory_manager.get_or_create_session(payload.session_id)
    history = memory_manager.get_history(session.session_id)

    try:
        response_text = await llm_service.generate_response(
            history=history,
            new_message=payload.message.strip()
        )
        
        # Record turn in session memory
        memory_manager.add_turn(
            session_id=session.session_id,
            user_text=payload.message.strip(),
            assistant_text=response_text
        )

        return ChatResponse(
            session_id=session.session_id,
            message=response_text,
            status="success",
            model=llm_service.get_model_name(),
            context_turn_count=len(memory_manager.get_history(session.session_id))
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "session_id": session.session_id,
                "message": f"RUHI encountered an unexpected error: {str(e)}. Please check backend configuration.",
                "status": "error",
                "model": llm_service.get_model_name(),
                "context_turn_count": len(history)
            }
        )


@app.post("/api/chat/clear", response_model=ClearSessionResponse)
async def clear_session_endpoint(payload: ClearSessionRequest):
    """Resets the conversation context for the specified session."""
    success = memory_manager.clear_session(payload.session_id)
    return ClearSessionResponse(
        session_id=payload.session_id,
        status="cleared" if success else "not_found",
        message="Conversation context reset successfully."
    )


@app.get("/api/capabilities")
async def get_capabilities():
    """Returns structured metadata about RUHI's capabilities across Web and Desktop."""
    return {
        "categories": [
            {
                "id": "understand",
                "title": "Understand",
                "description": "Perceive multi-turn conversational intent, nuances, and constraints.",
                "features": [
                    {"title": "Natural Conversation", "status": "available_now"},
                    {"title": "Intent Extraction", "status": "available_now"},
                    {"title": "Contextual Dialogue", "status": "available_now"},
                    {"title": "Complex Multi-Step Requests", "status": "available_now"}
                ]
            },
            {
                "id": "remember",
                "title": "Remember",
                "description": "Retain session context and synthesize long-term personal knowledge.",
                "features": [
                    {"title": "Active Session Context", "status": "available_now"},
                    {"title": "User Preferences & State", "status": "coming_soon"},
                    {"title": "Cross-Session Memory", "status": "coming_soon"},
                    {"title": "Privacy-First Memory Inspector", "status": "coming_soon"}
                ]
            },
            {
                "id": "know",
                "title": "Know",
                "description": "Ground reasoning in personal documents and dynamic web intelligence.",
                "features": [
                    {"title": "Web Intelligence", "status": "available_now"},
                    {"title": "User Uploaded Documents", "status": "coming_soon"},
                    {"title": "Local Knowledge Indexing", "status": "desktop_only"},
                    {"title": "Semantic Document Search", "status": "desktop_only"}
                ]
            },
            {
                "id": "think",
                "title": "Think",
                "description": "Deconstruct complex objectives into reasoning chains and plans.",
                "features": [
                    {"title": "Goal Decomposition", "status": "available_now"},
                    {"title": "Step-by-Step Planning", "status": "available_now"},
                    {"title": "Tool Selection Logic", "status": "available_now"},
                    {"title": "Self-Correction Reasoning", "status": "coming_soon"}
                ]
            },
            {
                "id": "act",
                "title": "Act",
                "description": "Execute authorized actions, coordinate tools, and automate workflows.",
                "features": [
                    {"title": "Structured Workflow Planning", "status": "available_now"},
                    {"title": "Desktop Tool Execution", "status": "desktop_only"},
                    {"title": "Application Automation", "status": "desktop_only"},
                    {"title": "Permission-Guarded Actions", "status": "desktop_only"}
                ]
            },
            {
                "id": "create",
                "title": "Create",
                "description": "Synthesize documents, software code, creative concepts, and workflows.",
                "features": [
                    {"title": "Code & Architecture Generation", "status": "available_now"},
                    {"title": "Analytical Writing & Synthesis", "status": "available_now"},
                    {"title": "Local File Generation", "status": "desktop_only"},
                    {"title": "Multi-File Project Scaffolding", "status": "desktop_only"}
                ]
            }
        ],
        "tools": [t.dict() for t in tool_registry.list_tools()]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
