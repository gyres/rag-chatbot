def test_upload_document_success(api_client, fake_rag_service) -> None:
    response = api_client.post(
        "/upload",
        files={"file": ("sample.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "sample.txt"
    assert data["message"] == "Successfully processed 1 chunks from sample.txt."

    uploaded_file = fake_rag_service.uploaded_files[0]
    assert uploaded_file["source_name"] == "sample.txt"
    assert uploaded_file["exists_when_called"] is True


def test_upload_document_rejects_empty_filename(api_client) -> None:
    response = api_client.post(
        "/upload",
        files={"file": ("", b"hello world", "text/plain")},
    )

    assert response.status_code == 422


def test_upload_document_returns_400_for_value_error(api_client) -> None:
    response = api_client.post(
        "/upload",
        files={"file": ("bad.txt", b"bad content", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported test file."


def test_send_message_success(api_client, fake_rag_service) -> None:
    response = api_client.post(
        "/message",
        json={"message": "Summarise the document."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "Fake answer: Summarise the document."
    }
    assert fake_rag_service.messages == ["Summarise the document."]


def test_send_message_rejects_empty_message(api_client) -> None:
    response = api_client.post(
        "/message",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_reset_chat_success(api_client, fake_rag_service) -> None:
    response = api_client.post("/reset/chat")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Conversation history has been reset.",
    }
    assert fake_rag_service.reset_chat_called is True


def test_reset_documents_success(api_client, fake_rag_service) -> None:
    response = api_client.post("/reset/documents")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Document knowledge has been reset.",
    }
    assert fake_rag_service.reset_documents_called is True


def test_reset_all_success(api_client, fake_rag_service) -> None:
    response = api_client.post("/reset/all")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Both conversation history and document knowledge have been reset.",
    }
    assert fake_rag_service.reset_all_called is True

def test_upload_document_rejects_unsupported_file_type(api_client) -> None:
    response = api_client.post(
        "/upload",
        files={"file": ("sample.docx", b"hello world", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported file format: .docx. Supported formats: .pdf, .txt"
    )


def test_upload_document_rejects_large_file(api_client, fake_rag_service) -> None:
    large_content = b"a" * (11 * 1024 * 1024)

    response = api_client.post(
        "/upload",
        files={"file": ("large.txt", large_content, "text/plain")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "Uploaded file is too large. Maximum allowed size is 10 MB."
    )
    assert fake_rag_service.uploaded_files == []