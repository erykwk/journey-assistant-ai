# Używamy oficjalnego, pełnego obrazu Pythona jako "buildera"
# Pełny obraz zawiera narzędzia potrzebne do kompilacji pakietów
FROM python:3.12-slim as builder

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy tylko plik z zależnościami, żeby wykorzystać cache Dockera
COPY requirements.txt .

# Instalujemy zależności
# Używamy --no-cache-dir, żeby nie zaśmiecać obrazu
RUN pip install --no-cache-dir -r requirements.txt

# --- Etap finalny ---
# Używamy tego samego, lekkiego obrazu jako bazowego dla finalnej aplikacji
FROM python:3.12-slim

WORKDIR /app

# Kopiujemy zainstalowane zależności z etapu "builder"
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Kopiujemy kod źródłowy naszej aplikacji
COPY src/ ./src
COPY tests/ ./tests

# Ustawiamy PYTHONPATH, żeby Python widział nasz kod w katalogu /app
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:${PATH}"

# Domyślna komenda (możemy ją nadpisać w docker-compose lub Kubernetes)
# Uruchamia serwer MCP
CMD ["python", "-m", "src.server"]
