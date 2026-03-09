from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.settings import get_settings
from src.db.session import get_db
from src.schemas.notes import NoteCreate, NoteListResponse, NoteOut, NoteUpdate
from src.services.notes_service import (
    create_note,
    delete_note,
    get_note,
    list_notes,
    set_favorite,
    set_pin,
    update_note,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "",
    response_model=NoteOut,
    summary="Create a note",
    description="Create a new note with optional tags.",
    operation_id="create_note",
)
def create_note_endpoint(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteOut:
    """Create a new note."""
    note = create_note(
        db,
        title=payload.title,
        content=payload.content,
        pinned=payload.pinned,
        favorite=payload.favorite,
        tag_names=payload.tags,
    )
    return note


@router.get(
    "",
    response_model=NoteListResponse,
    summary="List/search notes",
    description="List notes with optional search query, tag filter, and pinned/favorite filters.",
    operation_id="list_notes",
)
def list_notes_endpoint(
    q: Optional[str] = Query(default=None, description="Search query (matches title/content)."),
    tag: Optional[str] = Query(default=None, description="Filter by a tag name."),
    pinned: Optional[bool] = Query(default=None, description="Filter by pinned flag."),
    favorite: Optional[bool] = Query(default=None, description="Filter by favorite flag."),
    limit: int = Query(default=None, ge=1, le=1000, description="Page size."),
    offset: int = Query(default=0, ge=0, description="Offset for pagination."),
    db: Session = Depends(get_db),
) -> NoteListResponse:
    """List notes with filters."""
    settings = get_settings()
    effective_limit = limit if limit is not None else settings.default_page_size
    effective_limit = min(effective_limit, settings.max_page_size)

    items, total = list_notes(
        db,
        query=q,
        tag=tag,
        pinned=pinned,
        favorite=favorite,
        limit=effective_limit,
        offset=offset,
    )
    return NoteListResponse(items=items, total=total, limit=effective_limit, offset=offset)


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Fetch a single note by ID.",
    operation_id="get_note",
)
def get_note_endpoint(note_id: UUID, db: Session = Depends(get_db)) -> NoteOut:
    """Get note by ID."""
    return get_note(db, note_id)


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update note fields (title/content/tags/pinned/favorite).",
    operation_id="update_note",
)
def update_note_endpoint(note_id: UUID, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteOut:
    """Update a note."""
    note = update_note(
        db,
        note_id=note_id,
        title=payload.title,
        content=payload.content,
        pinned=payload.pinned,
        favorite=payload.favorite,
        tag_names=payload.tags,
    )
    return note


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    description="Delete a note by ID.",
    operation_id="delete_note",
)
def delete_note_endpoint(note_id: UUID, db: Session = Depends(get_db)) -> dict:
    """Delete a note by ID."""
    delete_note(db, note_id)
    return {"status": "deleted", "id": str(note_id)}


@router.post(
    "/{note_id}/pin",
    response_model=NoteOut,
    summary="Pin/unpin a note",
    description="Set pinned state for a note.",
    operation_id="set_note_pin",
)
def set_note_pin_endpoint(
    note_id: UUID,
    pinned: bool = Query(..., description="Pinned state to set."),
    db: Session = Depends(get_db),
) -> NoteOut:
    """Set pinned state."""
    return set_pin(db, note_id=note_id, pinned=pinned)


@router.post(
    "/{note_id}/favorite",
    response_model=NoteOut,
    summary="Favorite/unfavorite a note",
    description="Set favorite state for a note.",
    operation_id="set_note_favorite",
)
def set_note_favorite_endpoint(
    note_id: UUID,
    favorite: bool = Query(..., description="Favorite state to set."),
    db: Session = Depends(get_db),
) -> NoteOut:
    """Set favorite state."""
    return set_favorite(db, note_id=note_id, favorite=favorite)
