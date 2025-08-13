from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI DDD Backend"
    }

@router.get("/ready")
async def readiness_check():
    # Add any readiness checks here (database connectivity, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }
