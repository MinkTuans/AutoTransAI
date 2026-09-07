from typing import Optional

from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    segment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("segments.id", ondelete="CASCADE"), nullable=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    asset_type: Mapped[str] = mapped_column(String(30))  # audio, video, merged, final
    file_path: Mapped[str] = mapped_column(String(500))
    file_format: Mapped[str] = mapped_column(String(10))  # wav, mp4
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Relationships
    segment: Mapped["Segment | None"] = relationship(back_populates="assets")  # type: ignore[name-defined]
