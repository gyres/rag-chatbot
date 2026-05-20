from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from rag_chatbot.api.endpoints import router as api_router
from rag_chatbot.web.pages import router as web_router

from types import SimpleNamespace


class FakeRAGService:
    def __init__(self) -> None:
        self.uploaded_files = []
        self.messages = []
        self.reset_chat_called = False
        self.reset_documents_called = False
        self.reset_all_called = False

    def upload_document(self, file_path, source_name=None) -> str:
        path = Path(file_path)

        self.uploaded_files.append(
            {
                "path": path,
                "source_name": source_name,
                "exists_when_called": path.exists(),
            }
        )

        if source_name == "bad.txt":
            raise ValueError("Unsupported test file.")

        return f"Successfully processed 1 chunks from {source_name}."

    def send_message(self, message: str) -> str:
        self.messages.append(message)
        return f"Fake answer: {message}"

    def reset_conversation(self) -> str:
        self.reset_chat_called = True
        return "Conversation history has been reset."

    def reset_documents(self) -> str:
        self.reset_documents_called = True
        return "Document knowledge has been reset."

    def reset_all(self) -> str:
        self.reset_all_called = True
        return "Both conversation history and document knowledge have been reset."


@pytest.fixture
def fake_rag_service() -> FakeRAGService:
    return FakeRAGService()


@pytest.fixture
def api_client(fake_rag_service: FakeRAGService) -> TestClient:
    app = FastAPI()
    app.state.settings = SimpleNamespace(max_upload_size_mb=10)
    app.state.rag_service = fake_rag_service
    app.include_router(api_router)

    return TestClient(app)


@pytest.fixture
def web_client() -> TestClient:
    app = FastAPI()

    project_root = Path(__file__).resolve().parents[1]
    static_dir = project_root / "src" / "rag_chatbot" / "web" / "static"

    app.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static",
    )

    app.include_router(web_router)

    return TestClient(app)