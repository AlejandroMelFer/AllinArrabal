FROM python:3.13-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY fastapi_server.py strings.json ./

CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]