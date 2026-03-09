from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import get_settings
from src.db.init_db import init_db

from src.api.routes.notes import router as notes_router
from src.api.routes.tags import router as tags_router

openapi_tags = [
    {
        "name": "system",
        "description": "Health checks and system endpoints.",
    },
    {
        "name": "notes",
        "description": "Notes CRUD, search, and pin/favorite operations.",
    },
    {
        "name": "tags",
        "description": "Tag management endpoints.",
    },
]

settings = get_settings()

app = FastAPI(
    title="NoteMaster Backend API",
    description=(
        "REST API for a fullstack notes application. Provides CRUD operations for notes, "
        "searching/filtering, tag management, and pin/favorite state."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS: allow frontend origins configured via FRONTEND_ORIGINS env var.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins() or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables on startup."""
    init_db()


@app.get(
    "/",
    tags=["system"],
    summary="Health check",
    description="Basic health check endpoint.",
    operation_id="health_check",
)
def health_check() -> dict:
    """Return a basic health check response."""
    return {"message": "Healthy"}


app.include_router(notes_router)
app.include_router(tags_router)
