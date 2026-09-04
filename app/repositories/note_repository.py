import select
from typing import List

from sqlmodel import Session

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
        return Notes
