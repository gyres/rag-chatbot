import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from rag_chatbot.api.schemas import (
    MessageRequest,
    MessageResponse,
    StatusResponse,
    UploadResponse,
)
from rag_chatbot.core.config import Settings, get_settings
from rag_chatbot.services.rag_service import RAGService


logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_FILE_SUFFIXES = {".pdf", ".txt"}
READ_CHUNK_SIZE = 1024 * 1024


def get_app_settings(request: Request) -> Settings:
    settings = getattr(request.app.state, "settings", None)

    if settings is None:
        settings = get_settings()
        request.app.state.settings = settings

    return settings


def get_rag_service(request: Request) -> RAGService:
    service = getattr(request.app.state, "rag_service", None)

    if service is None:
        settings = get_app_settings(request)
        service = RAGService.from_settings(settings)
        request.app.state.rag_service = service

    return service


async def save_upload_to_temp_file(
    file: UploadFile,
    suffix: str,
    max_size_bytes: int,
) -> Path:
    total_size = 0
    temp_file_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = Path(temp_file.name)

            while chunk := await file.read(READ_CHUNK_SIZE):
                total_size += len(chunk)

                if total_size > max_size_bytes:
                    max_size_mb = max_size_bytes // (1024 * 1024)
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail=(
                            f"Uploaded file is too large. "
                            f"Maximum allowed size is {max_size_mb} MB."
                        ),
                    )

                temp_file.write(chunk)

        return temp_file_path

    except Exception:
        if temp_file_path is not None:
            temp_file_path.unlink(missing_ok=True)

        raise


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_FILE_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format: {suffix}. "
                "Supported formats: .pdf, .txt"
            ),
        )

    settings = get_app_settings(request)
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    temp_file_path: Path | None = None

    try:
        temp_file_path = await save_upload_to_temp_file(
            file=file,
            suffix=suffix,
            max_size_bytes=max_size_bytes,
        )

        service = get_rag_service(request)
        message = service.upload_document(temp_file_path, source_name=file.filename)

        return UploadResponse(message=message, filename=file.filename)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Error processing uploaded document.")
        raise HTTPException(
            status_code=500,
            detail="Error processing document. Please try again.",
        ) from exc

    finally:
        if temp_file_path is not None:
            temp_file_path.unlink(missing_ok=True)


@router.post("/message", response_model=MessageResponse)
async def send_message(request: Request, payload: MessageRequest) -> MessageResponse:
    try:
        service = get_rag_service(request)
        response = service.send_message(payload.message)
        return MessageResponse(response=response)

    except Exception as exc:
        logger.exception("Error processing message.")
        raise HTTPException(
            status_code=500,
            detail="Error processing message. Please try again.",
        ) from exc


@router.post("/reset/chat", response_model=StatusResponse)
async def reset_chat(request: Request) -> StatusResponse:
    service = get_rag_service(request)
    return StatusResponse(message=service.reset_conversation())


@router.post("/reset/documents", response_model=StatusResponse)
async def reset_documents(request: Request) -> StatusResponse:
    service = get_rag_service(request)
    return StatusResponse(message=service.reset_documents())


@router.post("/reset/all", response_model=StatusResponse)
async def reset_all(request: Request) -> StatusResponse:
    service = get_rag_service(request)
    return StatusResponse(message=service.reset_all())