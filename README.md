# RAG Chatbot

A local Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, LangChain, OpenAI, FAISS, and Docker.

The application allows users to upload a PDF or TXT document, ask questions about the uploaded document, and receive answers grounded in retrieved document context.

## Screenshot

![RAG Chatbot frontend](docs/images/frontend.png)

## Features

- Upload and process PDF or TXT documents
- Split uploaded documents into searchable text chunks
- Store document embeddings in a FAISS vector store
- Retrieve relevant document chunks based on user questions
- Generate document-grounded answers using an OpenAI chat model
- Reset chat history, document knowledge, or both
- Simple web interface built with HTML, CSS, and JavaScript
- API endpoints built with FastAPI
- Containerised setup with Docker and Docker Compose
- Automated tests with pytest

## Tech Stack

- Python
- FastAPI
- LangChain
- OpenAI API
- FAISS
- Jinja2
- HTML, CSS, JavaScript
- Pydantic
- pytest
- Docker
- Docker Compose
- conda-forge

## Project Structure

```text
rag-chatbot/
├── README.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── environment.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── .vscode/
│   └── settings.json
├── docs/
│   └── images/
│       └── frontend.png
├── src/
│   └── rag_chatbot/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── endpoints.py
│       │   └── schemas.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── rag_service.py
│       │   ├── chat_engine.py
│       │   └── document_processor.py
│       └── web/
│           ├── __init__.py
│           ├── pages.py
│           ├── templates/
│           │   └── index.html
│           └── static/
│               ├── styles.css
│               └── app.js
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_api_endpoints.py
    ├── test_chat_engine.py
    ├── test_rag_service.py
    ├── test_schemas.py
    └── test_web_pages.py
```

## Setup

You can run this project using one of the following methods:

1. Docker with `docker-compose.yml`, recommended for the fastest reproducible setup.
2. Conda with `environment.yml`, recommended if you are using Anaconda or Miniconda.
3. Pip with `requirements.txt`, useful for standard Python virtual environments.

The commands below use Git Bash as the main terminal. PowerShell alternatives are shown only when the command syntax is different.

### 1. Clone the repository

```bash
git clone https://github.com/gyres/rag-chatbot.git
cd rag-chatbot
```

### 2. Create the environment variables file

Git Bash:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Then open `.env` and add your OpenAI API settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=your_chat_model_name_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.2

CHUNK_SIZE=1000
CHUNK_OVERLAP=100
RETRIEVAL_K=3
MAX_UPLOAD_SIZE_MB=10
```

Do not commit your real `.env` file to GitHub.

### 3. Choose one setup option

#### Option A: Run with Docker

Make sure Docker Desktop is installed and running.

```bash
docker compose up --build
```

To stop the application, press `Ctrl + C` in the terminal.

Then remove the stopped container:

```bash
docker compose down
```

#### Option B: Run with conda

Create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate rag-chatbot
```

If the environment already exists and you want to update it:

```bash
conda env update -f environment.yml --prune
conda activate rag-chatbot
```

Run the application.

Git Bash:

```bash
PYTHONPATH=src python -m uvicorn rag_chatbot.main:app --reload
```

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn rag_chatbot.main:app --reload
```

#### Option C: Run with pip

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

Git Bash:

```bash
source .venv/Scripts/activate
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the application.

Git Bash:

```bash
PYTHONPATH=src python -m uvicorn rag_chatbot.main:app --reload
```

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn rag_chatbot.main:app --reload
```

### 4. Open the application

Open the app in your browser:

```text
http://localhost:8000
```

## How to Use

1. Open the web app in your browser.
2. Upload a PDF or TXT document.
3. Wait for the document to be processed.
4. Ask a question about the uploaded document.
5. Use the reset buttons when needed:
   - Reset chat
   - Reset documents
   - Reset all

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Loads the web interface |
| `POST` | `/upload` | Uploads and processes a PDF or TXT document |
| `POST` | `/message` | Sends a user question and returns a RAG response |
| `POST` | `/reset/chat` | Clears conversation history |
| `POST` | `/reset/documents` | Clears uploaded document knowledge |
| `POST` | `/reset/all` | Clears both chat history and document knowledge |

## Running Tests

Run the test suite with:

```bash
python -m pytest
```

The tests cover:

- API upload and message endpoints
- Request and response schemas
- RAG service behaviour
- Chat engine behaviour
- Web page loading
- Reset routes
- File validation logic

## Current Limitations

- This is a learning and portfolio project, not a production system.
- Document knowledge is stored in memory and is reset when the app restarts.
- Uploaded documents are processed through temporary files and are not persisted after processing.
- The app currently supports PDF and TXT files only.
- There is no user authentication.
- The app uses one in-memory RAG service per running application process, so it is not designed for multi-user production use.
- The FAISS vector store is local and in-memory for this version.
- The chatbot is designed for retrieval-based question answering and does not currently support full-document summarisation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

- Name: Ou Yang Yu
- GitHub: https://github.com/gyres