"""AEGIS Stream Consumer Group & Partition Offset ORM Models.

Tracks consumer groups, partition assignments, current offsets, log end offsets, and lag.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional
from sqlalchemy import String, DateTime, Integer, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class StreamConsumerGroupModel(Base):
    """Consumer group entity."""

    __tablename__ = "stream_consumer_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    group_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    topic_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="STABLE")  # STABLE, REBALANCING, DEAD
    members_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_lag: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "group_id", "topic_name", name="uq_tenant_group_topic"),
    )


class StreamPartitionOffsetModel(Base):
    """Partition offset checkpoint entity."""

    __tablename__ = "stream_partition_offsets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_group_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("stream_consumer_groups.id", ondelete="CASCADE"),
        nullable=False
    )
    topic_name: Mapped[str] = mapped_column(String(128), nullable=False)
    partition_id: Mapped[int] = mapped_column(Integer, nullable=False)
    current_offset: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    log_end_offset: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    lag: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("consumer_group_id", "partition_id", name="uq_group_partition"),
    )
