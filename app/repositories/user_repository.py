from sqlmodel import Session, select

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    # * obtner el usuario
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
    # *obtner el usuario por el email

    def get_by_email(self, email: str) -> User | None:
        return self.db.exec(select(User).where(User.email == email)).first()

    # *crear el usuario

    def create(self, user: User) -> User:
        self.db.add(user)
        # self.db.flush()
        # * puede ri el commit desde aqui o no
        self.db.commit()
        self.db.refresh(user)
        return user
