FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "rag_chatbot.main:app", "--host", "0.0.0.0", "--port", "8000"]