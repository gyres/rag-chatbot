from pathlib import Path

from langchain_core.documents import Document

from rag_chatbot.services.rag_service import RAGService


class FakeDocumentProcessor:
    def __init__(self) -> None:
        self.process_calls = []
        self.retrieve_calls = []
        self.reset_called = False

    def process_document(self, file_path, source_name=None) -> int:
        self.process_calls.append((Path(file_path), source_name))
        return 2

    def retrieve_relevant_context(self, query: str, k: int = 3):
        self.retrieve_calls.append((query, k))

        return [
            Document(
                page_content="Transformers use self-attention.",
                metadata={"source": "attention.pdf", "page": 0},
            )
        ]

    def reset(self) -> None:
        self.reset_called = True


class FakeChatEngine:
    def __init__(self) -> None:
        self.sent_messages = []
        self.reset_called = False

    def send_message(self, message: str, context: str = "") -> str:
        self.sent_messages.append((message, context))
        return "Fake RAG answer."

    def reset_conversation(self) -> str:
        self.reset_called = True
        return "Conversation history has been reset."


def test_upload_document_processes_file_and_returns_message() -> None:
    processor = FakeDocumentProcessor()
    chat_engine = FakeChatEngine()
    service = RAGService(processor, chat_engine, retrieval_k=4)

    result = service.upload_document("sample.pdf", source_name="sample.pdf")

    assert result == "Successfully processed 2 chunks from sample.pdf."
    assert processor.process_calls == [(Path("sample.pdf"), "sample.pdf")]


def test_send_message_retrieves_context_and_calls_chat_engine() -> None:
    processor = FakeDocumentProcessor()
    chat_engine = FakeChatEngine()
    service = RAGService(processor, chat_engine, retrieval_k=4)

    result = service.send_message("What is self-attention?")

    assert result == "Fake RAG answer."
    assert processor.retrieve_calls == [("What is self-attention?", 4)]

    message, context = chat_engine.sent_messages[0]
    assert message == "What is self-attention?"
    assert "[Context 1 | attention.pdf, page 1]" in context
    assert "Transformers use self-attention." in context


def test_reset_conversation_calls_chat_engine() -> None:
    processor = FakeDocumentProcessor()
    chat_engine = FakeChatEngine()
    service = RAGService(processor, chat_engine)

    result = service.reset_conversation()

    assert result == "Conversation history has been reset."
    assert chat_engine.reset_called is True


def test_reset_documents_calls_document_processor() -> None:
    processor = FakeDocumentProcessor()
    chat_engine = FakeChatEngine()
    service = RAGService(processor, chat_engine)

    result = service.reset_documents()

    assert result == "Document knowledge has been reset."
    assert processor.reset_called is True


def test_reset_all_resets_chat_and_documents() -> None:
    processor = FakeDocumentProcessor()
    chat_engine = FakeChatEngine()
    service = RAGService(processor, chat_engine)

    result = service.reset_all()

    assert result == "Both conversation history and document knowledge have been reset."
    assert chat_engine.reset_called is True
    assert processor.reset_called is True