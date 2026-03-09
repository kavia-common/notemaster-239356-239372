from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagOut(BaseModel):
    """Serialized Tag."""

    id: UUID = Field(..., description="Tag ID.")
    name: str = Field(..., description="Unique tag name.")
    created_at: datetime = Field(..., description="Tag creation timestamp (UTC).")


class NoteBase(BaseModel):
    """Shared fields for note creation/update."""

    title: str = Field(default="", max_length=200, description="Note title.")
    content: str = Field(default="", description="Note content (markdown/plain text).")
    pinned: bool = Field(default=False, description="Whether the note is pinned.")
    favorite: bool = Field(default=False, description="Whether the note is favorited.")
    tags: List[str] = Field(default_factory=list, description="List of tag names.")


class NoteCreate(NoteBase):
    """Create note payload."""


class NoteUpdate(BaseModel):
    """Update note payload. All fields optional."""

    title: Optional[str] = Field(default=None, max_length=200, description="Note title.")
    content: Optional[str] = Field(default=None, description="Note content.")
    pinned: Optional[bool] = Field(default=None, description="Whether the note is pinned.")
    favorite: Optional[bool] = Field(default=None, description="Whether the note is favorited.")
    tags: Optional[List[str]] = Field(default=None, description="Replace tags with provided list.")


class NoteOut(BaseModel):
    """Serialized Note."""

    id: UUID = Field(..., description="Note ID.")
    title: str = Field(..., description="Note title.")
    content: str = Field(..., description="Note content.")
    pinned: bool = Field(..., description="Whether the note is pinned.")
    favorite: bool = Field(..., description="Whether the note is favorited.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC).")
    tags: List[TagOut] = Field(default_factory=list, description="Associated tags.")


class NoteListResponse(BaseModel):
    """Paginated-ish list response for notes."""

    items: List[NoteOut] = Field(..., description="Notes list.")
    total: int = Field(..., description="Total notes count for this query.")
    limit: int = Field(..., description="Returned page size limit.")
    offset: int = Field(..., description="Offset used.")
