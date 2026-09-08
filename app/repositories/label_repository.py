
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
