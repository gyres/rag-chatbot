def test_home_page_loads(web_client) -> None:
    response = web_client.get("/")

    assert response.status_code == 200
    assert "RAG Chatbot" in response.text
    assert "Upload a PDF or text file" in response.text
    assert "/static/styles.css" in response.text
    assert "/static/app.js" in response.text