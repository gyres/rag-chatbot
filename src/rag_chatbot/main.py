from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rag_chatbot.api.endpoints import router as api_router
from rag_chatbot.web.pages import router as web_router


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "web" / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Chatbot API")

    app.state.settings = None
    app.state.rag_service = None

    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

    app.include_router(web_router)
    app.include_router(api_router)

    return app


app = create_app()