import select
from typing import List

from sqlmodel import Session, delete

from app.models.label import NoteLabelLink
from app.models.notas import Notes


class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_owned(self, owner_id: int) -> List[Notes]:
        query = select(Notes).where(Notes.owner_id ==
                                    owner_id).order_by(Notes.id.desc())
        return self.db.exec(query).all()

    # *nota por id
    def get(self, note_id: int) -> Notes | None:
        return self.db.get(Notes, note_id)

    def create(self, note: Notes) -> Notes:
        self.db.add(note)
        self.commit()
        self.db.refresh(Notes)
        return note

    def update(self, note: Notes) -> Notes:
        self.db.add(note)
        self.commit()
        self.db.refresh(Notes)
        return note

    def delete(self, note: Notes) -> None:
        self.db.exec(delete(NoteLabelLink).where(
            NoteLabelLink.note_id == note.id))

    def replace_labels(self, owner_id: int, note_id: int, label_ids: list[int]) -> None:
        self.db.exec(delete(NoteLabelLink).where(
            NoteLabelLink.note_id == note_id))

        for label in set(label_ids or []):
            self.db.add(NoteLabelLink(note_id=note_id, label_id=label))

        self.db.commit()

    def list_by_ids(self, ids: list[int]) -> List[Note]:
        if not ids:
            return []

        return self.db.exec(select(Note).where(Note.id.in_(ids))).all()
