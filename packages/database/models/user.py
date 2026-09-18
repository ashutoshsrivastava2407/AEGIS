"""User Domain Database Model."""

from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class UserModel(AEGISBaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    permissions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
