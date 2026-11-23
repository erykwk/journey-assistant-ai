# Używamy oficjalnego, pełnego obrazu Pythona jako "buildera"
FROM python:3.12-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etap finalny ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY src/ ./src
COPY tests/ ./tests

ENV PYTHONPATH=/app

# Uvicorn będzie nasłuchiwał na wszystkich interfejsach na porcie 8000
EXPOSE 8000

# Komenda uruchamiająca serwer ASGI (Uvicorn)
# --host 0.0.0.0 jest kluczowe dla działania w kontenerze
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
