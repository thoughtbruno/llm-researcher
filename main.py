"""
Ponto de entrada principal da aplicação LLM API
Seguindo Clean Architecture e princípios SOLID
"""

import uvicorn
from app.core.app import app
from app.core.config import settings


def main() -> None:
    """
    Função principal para inicializar a aplicação
    Princípio: Single Responsibility
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )


if __name__ == "__main__":
    main()
