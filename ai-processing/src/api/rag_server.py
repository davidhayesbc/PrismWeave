#!/usr/bin/env python3
"""
PrismWeave RAG API Server
FastAPI server that provides RAG-enabled chat completions compatible with OpenAI API format
Can be used with Open WebUI, VS Code, and other clients
"""

import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError as e:
    print(f"ERROR: Required dependencies not installed: {e}")
    print("Please install with: pip install fastapi uvicorn")
    sys.exit(1)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from src.rag.rag_synthesizer import RAGSynthesizer, RAGQuery
    from src.models.ollama_client import OllamaClient
    from src.utils.config_simplified import get_config

    # Try to import LangChain RAG (optional enhancement)
    LANGCHAIN_AVAILABLE = False
    try:
        from src.rag.langchain_rag import LangChainRAGContext
        LANGCHAIN_AVAILABLE = True
        print("✅ LangChain integration available")
    except ImportError:
        print("ℹ️ LangChain not available - using standard RAG implementation")

except ImportError as e:
    print(f"ERROR: PrismWeave modules not found: {e}")
    print("Please ensure you're running from the correct directory and modules are available")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="prismweave-rag", description="Model to use")
    messages: List[Message] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    context_docs: Optional[int] = Field(default=10, description="Number of context documents for RAG")
    synthesis_style: Optional[str] = Field(default="comprehensive", description="RAG synthesis style")

class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: Message
    finish_reason: str = "stop"

class ChatCompletionResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = "chat.completion"
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used for completion")
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int] = Field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

class RAGConfigRequest(BaseModel):
    enabled: bool = Field(default=True, description="Enable RAG functionality")
    context_docs: int = Field(default=10, description="Number of context documents")
    synthesis_style: str = Field(default="comprehensive", description="Synthesis style")
    similarity_threshold: float = Field(default=0.6, description="Similarity threshold for context retrieval")
    use_langchain: bool = Field(default=False, description="Use LangChain RAG implementation")
    retriever_strategy: str = Field(default="multi_query", description="LangChain retriever strategy")
    conversation_memory: bool = Field(default=True, description="Enable conversation memory (LangChain only)")

class RAGStatusResponse(BaseModel):
    rag_enabled: bool
    vector_db_status: str
    available_models: List[str]
    current_config: Dict[str, Any]
    langchain_available: bool
    langchain_enabled: bool

# FastAPI app
app = FastAPI(
    title="PrismWeave RAG API",
    description="RAG-enabled chat completions API compatible with OpenAI format",
    version="1.0.0"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class ServerState:
    def __init__(self):
        self.rag_synthesizer: Optional[RAGSynthesizer] = None
        self.langchain_rag = None  # Will be initialized if LangChain is available
        self.ollama_client: Optional[OllamaClient] = None
        self.config = get_config()
        self.rag_enabled = True
        self.langchain_enabled = False
        self.rag_config = {
            "context_docs": 10,
            "synthesis_style": "comprehensive",
            "similarity_threshold": 0.6,
            "use_langchain": False,
            "retriever_strategy": "multi_query",
            "conversation_memory": True
        }

state = ServerState()

@app.on_event("startup")
async def startup():
    """Initialize RAG components on server startup"""
    try:
        logger.info("Starting PrismWeave RAG API Server...")

        # Initialize standard RAG synthesizer
        state.rag_synthesizer = RAGSynthesizer()
        await state.rag_synthesizer.initialize()

        # Initialize LangChain RAG if available
        if LANGCHAIN_AVAILABLE:
            try:
                # Import here to avoid conflicts with outer scope
                from src.rag.langchain_rag import LangChainRAGContext as LCRAGContext  # pylint: disable=import-outside-toplevel
                state.langchain_rag = LCRAGContext()
                async with state.langchain_rag:
                    logger.info("LangChain RAG initialized successfully")
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("LangChain RAG initialization failed: %s", e)
                state.langchain_rag = None

        # Initialize Ollama client
        state.ollama_client = OllamaClient()
        async with state.ollama_client:
            pass

        logger.info("RAG API Server initialized successfully")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to initialize RAG API Server: %s", e)
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on server shutdown"""
    try:
        if state.rag_synthesizer:
            await state.rag_synthesizer.cleanup()
        if state.ollama_client:
            await state.ollama_client.__aexit__(None, None, None)
        logger.info("RAG API Server shutdown complete")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error during shutdown: %s", e)

# OpenAI-compatible endpoints
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Create a chat completion, optionally using RAG for enhanced responses
    Compatible with OpenAI Chat Completions API format
    """
    try:
        # Extract the user's question from messages
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")

        latest_message = user_messages[-1].content

        # Generate response ID
        response_id = f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if state.rag_enabled and state.rag_synthesizer:
            # Use RAG for enhanced response
            rag_query = RAGQuery(
                question=latest_message,
                max_context_documents=state.rag_config["context_docs"],
                synthesis_style=state.rag_config["synthesis_style"]
            )

            rag_response = await state.rag_synthesizer.query(rag_query)
            response_content = rag_response.answer

            # Add source information if available
            if rag_response.sources:
                source_info = f"\n\n**Sources** ({len(rag_response.sources)} documents):\n"
                for i, source in enumerate(rag_response.sources[:3], 1):
                    title = source.metadata.get('title', 'Unknown')
                    source_info += f"{i}. {title}\n"
                response_content += source_info

        else:
            # Fallback to direct Ollama
            model_name = state.config.ollama.models.get('large', 'llama3.1:8b')

            # Build conversation context
            conversation = ""
            for msg in request.messages:
                conversation += f"{msg.role}: {msg.content}\n"
            conversation += "assistant:"

            result = await state.ollama_client.generate(
                model=model_name,
                prompt=conversation,
                options={
                    'temperature': request.temperature,
                    'num_predict': request.max_tokens
                }
            )
            response_content = result.response

        # Create OpenAI-compatible response
        response = ChatCompletionResponse(
            id=response_id,
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    message=Message(role="assistant", content=response_content)
                )
            ]
        )

        return response

    except Exception as e:
        logger.error("Chat completion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    try:
        models = []

        # Add RAG-enabled model
        models.append({
            "id": "prismweave-rag",
            "object": "model",
            "created": int(datetime.now().timestamp()),
            "owned_by": "prismweave",
            "permission": [],
            "root": "prismweave-rag",
            "parent": None
        })

        # Add configured Ollama models
        for purpose, model_name in state.config.ollama.models.items():
            models.append({
                "id": f"{model_name}-{purpose}",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "ollama",
                "permission": [],
                "root": model_name,
                "parent": None
            })

        return {"object": "list", "data": models}

    except Exception as e:
        logger.error("Failed to list models: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

# PrismWeave-specific endpoints
@app.get("/rag/status", response_model=RAGStatusResponse)
async def get_rag_status():
    """Get RAG system status"""
    try:
        # Check vector DB status
        vector_status = "unknown"
        if state.rag_synthesizer and state.rag_synthesizer.search_engine:
            try:
                # Try a simple operation to check if vector DB is accessible
                await state.rag_synthesizer.search_engine.get_document_count()
                vector_status = "healthy"
            except Exception:  # pylint: disable=broad-exception-caught
                vector_status = "error"

        # Get available models
        available_models = []
        if state.ollama_client:
            try:
                models_info = await state.ollama_client.list_models()
                available_models = [model.name for model in models_info]
            except Exception:  # pylint: disable=broad-exception-caught
                available_models = ["unknown"]

        return RAGStatusResponse(
            rag_enabled=state.rag_enabled,
            vector_db_status=vector_status,
            available_models=available_models,
            current_config=state.rag_config
        )

    except Exception as e:
        logger.error("Failed to get RAG status: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/rag/config")
async def update_rag_config(config: RAGConfigRequest):
    """Update RAG configuration"""
    try:
        state.rag_enabled = config.enabled
        state.rag_config = {
            "context_docs": config.context_docs,
            "synthesis_style": config.synthesis_style,
            "similarity_threshold": config.similarity_threshold
        }

        return {"status": "success", "message": "RAG configuration updated", "config": state.rag_config}

    except Exception as e:
        logger.error("Failed to update RAG config: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/rag/ask")
async def ask_rag_question(request: Dict[str, Any]):
    """Direct RAG question endpoint"""
    try:
        question = request.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        style = request.get("style", "comprehensive")
        context_docs = request.get("context_docs", 10)

        if not state.rag_synthesizer:
            raise HTTPException(status_code=503, detail="RAG system not available")

        # Create RAG query
        rag_query = RAGQuery(
            question=question,
            max_context_documents=context_docs,
            synthesis_style=style
        )

        # Get response
        rag_response = await state.rag_synthesizer.query(rag_query)

        # Format response
        return {
            "question": rag_response.question,
            "answer": rag_response.answer,
            "confidence": rag_response.confidence_score,
            "processing_time": rag_response.processing_time,
            "source_count": rag_response.context_document_count,
            "sources": [
                {
                    "title": source.metadata.get('title', 'Unknown'),
                    "similarity": source.similarity_score,
                    "document_path": source.document_path
                }
                for source in rag_response.sources[:5]  # Limit to top 5 sources
            ]
        }

    except Exception as e:
        logger.error("RAG question failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        checks = {
            "api_server": "healthy",
            "rag_synthesizer": "healthy" if state.rag_synthesizer else "unavailable",
            "ollama_client": "healthy" if state.ollama_client else "unavailable",
            "vector_db": "unknown"
        }

        # Check vector DB
        if state.rag_synthesizer and state.rag_synthesizer.search_engine:
            try:
                await state.rag_synthesizer.search_engine.get_document_count()
                checks["vector_db"] = "healthy"
            except Exception:  # pylint: disable=broad-exception-caught
                checks["vector_db"] = "error"

        all_healthy = all(status in ["healthy", "unknown"] for status in checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Health check failed: %s", e)
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Development server startup
def main():
    """Run the development server"""
    parser = argparse.ArgumentParser(description="PrismWeave RAG API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    print(f"Starting PrismWeave RAG API Server on {args.host}:{args.port}")
    print(f"OpenAI-compatible endpoint: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"RAG status endpoint: http://{args.host}:{args.port}/rag/status")
    print(f"Health check: http://{args.host}:{args.port}/health")

    uvicorn.run(
        "rag_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
