from fastapi import FastAPI
from src.api.health import router as health_router

app = FastAPI(
    title="Travel Agent Planner - Backend",
    description="Główny serwis backendowy z pętlą agentową.",
    version="0.1.0",
)

# Dołączamy routery z poszczególnych modułów
# Prefix /api/v1 będzie obowiązywał dla wszystkich ścieżek z tego routera
app.include_router(health_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    """Główny endpoint, weryfikujący działanie aplikacji."""
    return {"message": "Welcome to Travel Agent Planner API "}
