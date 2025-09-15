from pydantic_settings import BaseSettings
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router, llm_router

class Settings(BaseSettings):
    """
    Configurações da aplicação
    Seguindo o princípio de Single Responsibility
    """
    
    # Configurações da API
    API_TITLE: str = "LLM API"
    API_DESCRIPTION: str = "API para aplicação LLM seguindo Clean Architecture"
    API_VERSION: str = "1.0.0"
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # Configurações de CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    
    # Configurações de logs
    LOG_LEVEL: str = "info"
    
    # Configurações de LLM (opcionais)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite campos extras do .env


# Instância global das configurações (Singleton pattern)
settings = Settings()



def _setup_middlewares(app: FastAPI) -> None:
    """
    Configura os middlewares da aplicação
    Princípio: Single Responsibility
    """
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )


def _setup_routes(app: FastAPI) -> None:
    """
    Configura as rotas da aplicação
    Princípio: Single Responsibility
    """
    
    
    # Incluir rotas principais
    app.include_router(api_router)
    
    # Incluir rotas específicas de LLM
    app.include_router(llm_router)

