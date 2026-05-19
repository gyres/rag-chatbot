from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from rag_chatbot.core.config import Settings
from rag_chatbot.services.chat_engine import ChatEngine
from rag_chatbot.services.document_processor import DocumentProcessor


class RAGService:
    def __init__(
        self,
        document_processor: DocumentProcessor,
        chat_engine: ChatEngine,
        retrieval_k: int = 3,
    ) -> None:
        self.document_processor = document_processor
        self.chat_engine = chat_engine
        self.retrieval_k = retrieval_k

    @classmethod
    def from_settings(cls, settings: Settings) -> "RAGService":
        chat_model = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
        )

        embedding_model = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

        document_processor = DocumentProcessor(
            embedding_model=embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        chat_engine = ChatEngine(chat_model=chat_model)

        return cls(
            document_processor=document_processor,
            chat_engine=chat_engine,
            retrieval_k=settings.retrieval_k,
        )

    def upload_document(self, file_path: str | Path, source_name: str | None = None) -> str:
        chunk_count = self.document_processor.process_document(file_path, source_name)
        display_name = source_name or Path(file_path).name
        return f"Successfully processed {chunk_count} chunks from {display_name}."

    def send_message(self, message: str) -> str:
        relevant_docs = self.document_processor.retrieve_relevant_context(
            message,
            k=self.retrieval_k,
        )
        context = self._format_context(relevant_docs)
        return self.chat_engine.send_message(message, context)

    def reset_conversation(self) -> str:
        return self.chat_engine.reset_conversation()

    def reset_documents(self) -> str:
        self.document_processor.reset()
        return "Document knowledge has been reset."

    def reset_all(self) -> str:
        self.reset_conversation()
        self.reset_documents()
        return "Both conversation history and document knowledge have been reset."

    @staticmethod
    def _format_context(documents: list[Document]) -> str:
        formatted_chunks = []

        for index, doc in enumerate(documents, start=1):
            source = doc.metadata.get("source", "unknown source")
            page = doc.metadata.get("page")
            page_label = f", page {page + 1}" if isinstance(page, int) else ""

            formatted_chunks.append(
                f"[Context {index} | {source}{page_label}]\n{doc.page_content}"
            )

        return "\n\n".join(formatted_chunks)