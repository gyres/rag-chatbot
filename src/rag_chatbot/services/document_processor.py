from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    def __init__(
        self,
        embedding_model: OpenAIEmbeddings,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> None:
        self.embedding_model = embedding_model
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.vectorstore: FAISS | None = None

    def load_document(self, file_path: str | Path) -> list[Document]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))
        elif suffix == ".txt":
            loader = TextLoader(str(path), encoding="utf-8")
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. Supported formats: .pdf, .txt"
            )

        return loader.load()

    def process_document(self, file_path: str | Path, source_name: str | None = None) -> int:
        docs = self.load_document(file_path)
        source = source_name or Path(file_path).name

        for doc in docs:
            doc.metadata["source"] = source

        split_docs = self.text_splitter.split_documents(docs)

        if not split_docs:
            raise ValueError("No readable text was found in the uploaded document.")

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(split_docs, self.embedding_model)
        else:
            self.vectorstore.add_documents(split_docs)

        return len(split_docs)

    def retrieve_relevant_context(self, query: str, k: int = 3) -> list[Document]:
        if self.vectorstore is None:
            return []

        return self.vectorstore.similarity_search(query, k=k)

    def reset(self) -> None:
        self.vectorstore = None