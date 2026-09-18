"""Tenant Domain Database Model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class TenantModel(AEGISBaseModel):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(50), default="ENTERPRISE", nullable=False)
    encryption_key_id: Mapped[str] = mapped_column(String(255), nullable=True)
