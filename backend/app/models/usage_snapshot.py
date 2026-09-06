from typing import Optional

from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UsageSnapshot(Base):
    __tablename__ = "usage_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("providers.id"), index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50))
    # e.g. "characters", "credits", "input_tokens", "video_seconds"
    used: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    limit_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    remaining: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
