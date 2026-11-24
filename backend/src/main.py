from fastapi import FastAPI
from src.api.health import router as health_router
from src.api.agent import router as agent_router

app = FastAPI(
    title="Travel Agent Planner - Backend",
    description="Główny serwis backendowy z pętlą agentową.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Travel Agent Planner API"}