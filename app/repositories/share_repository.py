from sqlmodel import Session, false, select, delete

from app.models.share import LabelShare, NoteShare


class ShareRepository:

    def __init__(self, db: Session):
        self.db = db

    def upsert_note_share(self, note_id: int, user_id: int, role: str) -> NoteShare:
        share = self.db.exec(select(NoteShare).where(
            NoteShare.note_id == note_id, NoteShare.user_id == user_id)).first()

        if share:
            share.role = role
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            return share
        share = NoteShare(note_id=note_id, user_id=user_id, role=role)
        self.db.add(share)

    def remove_note_share(self, note_id: int, user_id: int) -> None:
        self.db.exec(delete(NoteShare).where(NoteShare.note_id ==
                     note_id, NoteShare.user_id == user_id))
        self.db.commit()

    # * compartir etiqueta

    def upsert_label_share(self, label_id: int, user_id: int, role: str) -> LabelShare:
        share = self.db.exec(select(LabelShare).where(
            LabelShare.labe_id == label_id, LabelShare.user_id == user_id)).first()

        if share:
            share.role = role
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            return share
        share = LabelShare(labe_id=label_id, user_id=user_id, role=role)
        self.db.add(share)

    def remove_label_share(self, label_id: int, user_id: int) -> None:
        self.db.exec(delete(LabelShare).where(LabelShare.label_id ==
                     label_id, LabelShare.user_id == user_id))
        self.db.commit()

    # si esta compartida o no
    def has_note_share(self, note_id: int, user_id: int, role: str | None = None) -> bool:
        query = select(NoteShare).where(
            NoteShare.note_id == note_id,
            NoteShare.user_id == user_id
        )

        if role is not None:
            query = query.where(NoteShare.role == role)

        return self.db.exec(query).first() is not None

    def has_any_label_share(self, label_ids: list[int], user_id: int, role: str | None = None):
        if not label_ids:
            return False

        query = select(LabelShare).where(
            LabelShare.label_id.in_(label_ids),
            LabelShare.user_id == user_id
        )

        if role is not None:
            query = query.where(LabelShare.role == role)

        return self.db.exec(query).first() is not None
