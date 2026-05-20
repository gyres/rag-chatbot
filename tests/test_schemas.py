import pytest
from pydantic import ValidationError

from rag_chatbot.api.schemas import (
    MessageRequest,
    MessageResponse,
    StatusResponse,
    UploadResponse,
)


def test_message_request_accepts_non_empty_message() -> None:
    request = MessageRequest(message="What is this document about?")

    assert request.message == "What is this document about?"


def test_message_request_rejects_empty_message() -> None:
    with pytest.raises(ValidationError):
        MessageRequest(message="")


def test_message_response_stores_response_text() -> None:
    response = MessageResponse(response="This is a test response.")

    assert response.response == "This is a test response."


def test_status_response_defaults_to_success() -> None:
    response = StatusResponse(message="Done.")

    assert response.status == "success"
    assert response.message == "Done."


def test_upload_response_extends_status_response() -> None:
    response = UploadResponse(message="Uploaded.", filename="sample.pdf")

    assert response.status == "success"
    assert response.message == "Uploaded."
    assert response.filename == "sample.pdf"