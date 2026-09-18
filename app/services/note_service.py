
from typing import List

from sqlmodel import Session

from app.models.notas import Notes
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
