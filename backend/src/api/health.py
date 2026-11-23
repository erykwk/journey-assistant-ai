from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Monitoring"])
def get_health_status():
    """Zwraca status serwisu, potwierdzając, że aplikacja działa."""
    return {"status": "ok"}
