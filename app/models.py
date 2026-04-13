from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key = True)
    username: so.Mapped[str] = so.mapped_column(unique = True, nullable = False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column()
    email: so.Mapped[str] = so.mapped_column(nullable = False)
