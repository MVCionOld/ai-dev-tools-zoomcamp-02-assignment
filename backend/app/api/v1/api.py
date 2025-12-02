"""Aggregate API router for version 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import executors, health, sessions

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(executors.router, prefix="/executors", tags=["executors"])
