from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.notes import TagOut
from src.services.notes_service import delete_tag, list_tags, rename_tag

router = APIRouter(prefix="/tags", tags=["tags"])


class TagRenameRequest(BaseModel):
    """Payload for renaming a tag."""

    name: str = Field(..., description="New tag name.")


@router.get(
    "",
    response_model=List[TagOut],
    summary="List tags",
    description="List all tags.",
    operation_id="list_tags",
)
def list_tags_endpoint(db: Session = Depends(get_db)) -> List[TagOut]:
    """List all tags."""
    return list_tags(db)


@router.put(
    "/{tag_id}",
    response_model=TagOut,
    summary="Rename a tag",
    description="Rename a tag by ID.",
    operation_id="rename_tag",
)
def rename_tag_endpoint(tag_id: UUID, payload: TagRenameRequest, db: Session = Depends(get_db)) -> TagOut:
    """Rename a tag."""
    return rename_tag(db, tag_id=tag_id, new_name=payload.name)


@router.delete(
    "/{tag_id}",
    summary="Delete a tag",
    description="Delete a tag by ID.",
    operation_id="delete_tag",
)
def delete_tag_endpoint(tag_id: UUID, db: Session = Depends(get_db)) -> dict:
    """Delete a tag."""
    delete_tag(db, tag_id)
    return {"status": "deleted", "id": str(tag_id)}
