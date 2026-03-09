from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.db.models import Note, Tag


def _normalize_tag(name: str) -> str:
    return name.strip().lower()


def _get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    normalized = [_normalize_tag(t) for t in tag_names if t and t.strip()]
    unique = sorted(set(normalized))
    if not unique:
        return []

    existing = db.execute(select(Tag).where(Tag.name.in_(unique))).scalars().all()
    existing_by_name = {t.name: t for t in existing}

    tags: List[Tag] = []
    for n in unique:
        if n in existing_by_name:
            tags.append(existing_by_name[n])
        else:
            tag = Tag(name=n)
            db.add(tag)
            tags.append(tag)
    return tags


def _note_to_out(note: Note) -> Note:
    # relationships are loaded via selectin
    return note


# PUBLIC_INTERFACE
def create_note(
    db: Session,
    *,
    title: str,
    content: str,
    pinned: bool,
    favorite: bool,
    tag_names: List[str],
) -> Note:
    """Create a note with optional tags."""
    note = Note(
        title=title or "",
        content=content or "",
        pinned=bool(pinned),
        favorite=bool(favorite),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    note.tags = _get_or_create_tags(db, tag_names)

    db.add(note)
    db.commit()
    db.refresh(note)
    return _note_to_out(note)


# PUBLIC_INTERFACE
def get_note(db: Session, note_id: UUID) -> Note:
    """Get note by id or raise 404."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return _note_to_out(note)


# PUBLIC_INTERFACE
def update_note(
    db: Session,
    *,
    note_id: UUID,
    title: Optional[str] = None,
    content: Optional[str] = None,
    pinned: Optional[bool] = None,
    favorite: Optional[bool] = None,
    tag_names: Optional[List[str]] = None,
) -> Note:
    """Update note fields and/or replace tags."""
    note = get_note(db, note_id)

    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    if pinned is not None:
        note.pinned = pinned
    if favorite is not None:
        note.favorite = favorite
    if tag_names is not None:
        note.tags = _get_or_create_tags(db, tag_names)

    note.updated_at = datetime.utcnow()

    db.add(note)
    db.commit()
    db.refresh(note)
    return _note_to_out(note)


# PUBLIC_INTERFACE
def delete_note(db: Session, note_id: UUID) -> None:
    """Delete note."""
    note = get_note(db, note_id)
    db.delete(note)
    db.commit()


# PUBLIC_INTERFACE
def list_notes(
    db: Session,
    *,
    query: Optional[str] = None,
    tag: Optional[str] = None,
    pinned: Optional[bool] = None,
    favorite: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Note], int]:
    """List/search notes with optional filters."""
    stmt = select(Note).distinct()
    count_stmt = select(func.count(func.distinct(Note.id)))

    if query:
        q = f"%{query.strip()}%"
        predicate = or_(Note.title.ilike(q), Note.content.ilike(q))
        stmt = stmt.where(predicate)
        count_stmt = count_stmt.where(predicate)

    if tag:
        t = _normalize_tag(tag)
        stmt = stmt.join(Note.tags).where(Tag.name == t)
        count_stmt = count_stmt.select_from(Note).join(Note.tags).where(Tag.name == t)

    if pinned is not None:
        stmt = stmt.where(Note.pinned == pinned)
        count_stmt = count_stmt.where(Note.pinned == pinned)

    if favorite is not None:
        stmt = stmt.where(Note.favorite == favorite)
        count_stmt = count_stmt.where(Note.favorite == favorite)

    stmt = stmt.order_by(Note.pinned.desc(), Note.favorite.desc(), Note.updated_at.desc()).limit(limit).offset(offset)

    items = db.execute(stmt).scalars().all()
    total = db.execute(count_stmt).scalar_one()
    return items, int(total)


# PUBLIC_INTERFACE
def set_pin(db: Session, *, note_id: UUID, pinned: bool) -> Note:
    """Set pinned flag."""
    return update_note(db, note_id=note_id, pinned=pinned)


# PUBLIC_INTERFACE
def set_favorite(db: Session, *, note_id: UUID, favorite: bool) -> Note:
    """Set favorite flag."""
    return update_note(db, note_id=note_id, favorite=favorite)


# PUBLIC_INTERFACE
def list_tags(db: Session) -> List[Tag]:
    """List tags ordered by name."""
    return db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all()


# PUBLIC_INTERFACE
def rename_tag(db: Session, *, tag_id: UUID, new_name: str) -> Tag:
    """Rename a tag."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    normalized = _normalize_tag(new_name)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tag name cannot be empty")

    existing = db.execute(select(Tag).where(Tag.name == normalized, Tag.id != tag_id)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag name already exists")

    tag.name = normalized
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# PUBLIC_INTERFACE
def delete_tag(db: Session, tag_id: UUID) -> None:
    """Delete a tag (associations will be removed via cascade)."""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    db.delete(tag)
    db.commit()
