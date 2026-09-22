
from typing import List

from fastapi import HTTPException
from sqlmodel import Session

from app.models.notas import NoteCreate, NoteUpdate, Notes
from app.models.share import ShareRole
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.share_repository import ShareRepository


class NoteService:
    def __init__(self, db: Session):
        self.db = db
        self.notes = NoteRepository(db)
        self.labels = LabelRepository(db)
        self.shares = ShareRepository(db)

    # permisos
    def user_can_read(self, user_id: int, note: Notes) -> bool:
        if note.owner_id == user_id:
            return True
        # si tienes la nota compartida
        if self.shares.has_note_share(note_id=note.id, user_id=user_id):
            return True
        # solo lectura

        labels_ids = self.labels.list_label_ids_for_note(note.id)
        return self.shares.has_any_label_share(label_ids=labels_ids, user_id=user_id)

    def user_can_edit(self, user_id: int, note: Notes) -> bool:

        if note.owner_id == user_id:
            return True

        if self.shares.has_note_share(note_id=note.id, user_id=user_id, role=ShareRole.EDIT):
            return True

        labels_ids = self.labels.list_label_ids_for_note(note.id)
        return self.shares.has_any_label_share(label_ids=labels_ids, user_id=user_id, role=ShareRole.EDIT)

    def list_visible(self, user_id: int) -> List[Notes]:

        owned = self.notes.list_owned(user_id)

        direct_ids = self.shares.lis_note_ids_shared_directely(user_id)

        shared_label_ids = self.shares.list_label_ids_shared_whit_user(user_id)
        ids_by_label = self.labels.list_note_ids_by_label_ids(shared_label_ids)

        combined_ids = list({*direct_ids, *ids_by_label})
        shared = self.notes.list_by_ids(combined_ids)

        combined = {note.id: note for note in owned}

        for note in shared:
            combined.setdefault(note.id, note)
        return sorted(combined.values(), key=lambda note: note.id, reverse=True)

    def create(self, owner_id: int, payload: NoteCreate) -> Notes:
        note = self.notes.create(
            Notes(owner_id=owner_id, **
                  payload.model_dump(exclude={'label_ids'}))
        )

        if payload.label_ids:
            self._set_labels(owner_id, note.id, payload.label_ids)

        return note

    def update(self, user_id: int, note_id: int, payload: NoteUpdate) -> Notes:

        note = self.notes.get(note_id)

        if not note:
            raise HTTPException(status_code=404, detail="Nota no encontrada")

        if not self.user_can_edit(user_id, note):
            raise HTTPException(status_code=403, detail="No autorizado")

        updates = payload.model_dump(exclude_none=True)
        label_ids = updates.pop("label_ids", None)

        for key, values in updates.items():
            setattr(note, key, values)
        note = self.notes.update(note)

        if label_ids is not None:
            if note.owner_id != user_id:
                raise HTTPException(
                    status_code=404, detail="Noexiste o no autorizado")
            self._set_labels(user_id, note.id, label_ids)
        return note

    def delete(self, user_id: int, note_id) -> None:
        note = self.notes.get(note_id)

        if not note or note.owner_id != user_id:
            raise HTTPException(
                status_code=404, detail="No existe la nota o no autorizado")

        self.notes.delete(note)

    # *helpers->asignar lasetiquetas a una nota

    def _set_labels(self, owner_id: int, note_id: int, label_ids: list[int]) -> None:
        valids_ids = self.labels.list_ids_for_owner_subset(
            owner_id, label_ids or []
        )
        self.notes.replace_labels(owner_id, note_id, valids_ids)
