from cProfile import label
from typing import List
from sqlmodel import Session, select, delete
from app.models.label import NoteLabelLink, Label
from app.models.share import LabelShare


class LabelRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_users(self, owner_id: int) -> list[Label]:
        query = select(Label).where(Label.owner_id ==
                                    owner_id).order_by(Label.name.asc())
        return self.db.exec(query).all()

    def get(self, label_id: int) -> Label | None:
        return self.db.get(Label, label_id)

    # *por  nombres
    def get_by_name(self, owner_id: int, name: str) -> Label | None:
        query = select(Label).where(Label.owner_id ==
                                    owner_id, Label.name == name)

        return self.db.exec(query).first()

    def create(self, owner_id: int, name: str) -> Label:
        label = Label(owner_id=owner_id, name=name)
        self.db.add(label)
        self.db.commit()
        self.db.refresh(label)
        return label

    def delete(self, label: Label) -> None:
        # *eliminar relaciones existentes
        self.db.exec(delete(NoteLabelLink).where(
            NoteLabelLink.label_id == label.id))
        self.db.exec(delete(LabelShare).where(LabelShare.label_id == label.id))
        # *eliminar la lebel
        self.db.delete(label)
        self.db.commit()

    """
    3 tres funciones para devolver a un solo oner y a una etiqueta 
    """

    def list_ids_for_owner_subset(self, owner_id: int, ids: list[int]) -> List[int]:
        if not ids:
            return []

        return self.db.exec(
            select(Label.id).where(Label.owner_id ==
                                   owner_id, Label.id.in_(set(ids)))
        ).all()

# devolver los id de una nota
    def list_label_ids_for_note(self, note_id: int) -> List[int]:
        return self.db.exec(
            select(NoteLabelLink.label_id).where(
                NoteLabelLink.note_id == note_id)
        ).scalars().all()
    # id para devolver cualquier iod  listadas

    def list_note_ids_by_label_ids(self, label_ids: List[int]) -> List[int]:
        if not label_ids:
            return []
        return self.db.exec(
            select(NoteLabelLink.note_id).where(
                NoteLabelLink.label_id.in_(label_ids)
            ).scalars().all()
        )
