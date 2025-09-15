from fastapi import FastAPI
from app.core.config import settings, _setup_middlewares, _setup_routes
from app.api.routes import api_router, llm_router

def create_application() -> FastAPI:
    """
    Factory para criar e configurar a aplicação FastAPI
    Seguindo o princípio de Single Responsibility e Dependency Inversion
    """
    
    # Criar instância do FastAPI
    application = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar middlewares
    _setup_middlewares(application)
    
    # Configurar rotas
    _setup_routes(application)
    
    return application



# Criar a aplicação (pode ser importada diretamente)
app = create_application()
