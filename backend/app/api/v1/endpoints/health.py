"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="Service health probe")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
