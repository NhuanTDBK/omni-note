from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.adapters.persistance.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.user_id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def get_all_users(self) -> List[User]:
        return self.session.query(User).all()

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.session.commit()
        return user

    def update_last_login(self, user_id: str) -> Optional[User]:
        return self.update_user(user_id, last_login=datetime.utcnow())

    def delete_user(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False
