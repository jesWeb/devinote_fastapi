from fastapi import HTTPException
from sqlmodel import Session

from app.models.share import ShareRole
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.share_repository import ShareRepository


class ShareService:
    def __init__(self, db: Session):
        self.shares = ShareRepository(db)
        self.notes = NoteRepository(db)
        self.labels = LabelRepository(db)

    def share_note(self, owner_id: int, note_id, tarjet_user_id: int, role: ShareRole):
        note = self.notes.get(note_id)

        if not note or note.owner_id != owner_id:
            raise HTTPException(
                status_code=404, detail="Nota no encontrada o no autorizada")

        shared = self.shares.upsert_note_share(
            note_id, tarjet_user_id, role.value if hasattr(role, "value")else role)

        return shared

    def dejar_compatir(self, owner_id: int, note_id: int, target_user_id: int):

        note = self.notes.get(note_id)

        if not note or note.owner_id != owner_id:
            raise HTTPException(
                status_code=404, detail="Nota no encontrada o no autorizada")

        self.shares.remove_note_share(note_id, target_user_id)
