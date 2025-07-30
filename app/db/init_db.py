from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import get_password_hash
from app.db import base


def init_db(db: Session) -> None:
    user = (
        db.query(models.User)
        .filter(models.User.email == settings.FIRST_SUPERUSER)
        .first()
    )
    if not user:
        user_in = models.User(
            email=settings.FIRST_SUPERUSER,
            username="admin",
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="System Administrator",
            is_superuser=True,
            is_active=True,
        )
        db.add(user_in)
        db.commit()
        db.refresh(user_in)
