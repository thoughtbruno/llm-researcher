from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime


# Router principal da API
api_router = APIRouter()


@api_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    description="Endpoint principal da API"
)
async def root() -> Dict[str, Any]:
    """
    Endpoint raiz da API
    Retorna informações básicas sobre o serviço
    """
    return {
        "message": "LLM API está funcionando!",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@api_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica o status de saúde da aplicação"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Usado para monitoramento e verificação de disponibilidade
    """
    return {
        "status": "healthy",
        "service": "LLM API",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running"
    }


# Router para endpoints específicos de LLM (para expansão futura)
llm_router = APIRouter(prefix="/llm", tags=["LLM"])


@llm_router.get(
    "/models",
    status_code=status.HTTP_200_OK,
    summary="List available models",
    description="Lista os modelos de LLM disponíveis"
)
async def list_models() -> Dict[str, Any]:
    """
    Lista os modelos de LLM disponíveis
    """
    return {
        "models": [
            {"name": "gpt-3.5-turbo", "provider": "openai", "status": "available"},
            {"name": "claude-3", "provider": "anthropic", "status": "available"},
        ],
        "total": 2
    }


@llm_router.post(
    "/chat",
    status_code=status.HTTP_200_OK,
    summary="Chat with LLM",
    description="Endpoint para chat com modelos LLM"
)
async def chat_with_llm() -> Dict[str, Any]:
    """
    Endpoint para chat com LLM
    (Implementação futura)
    """
    return {
        "message": "Chat endpoint - Em desenvolvimento",
        "status": "not_implemented"
    }
