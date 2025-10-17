from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    os: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    scans: Mapped[list[Scan]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    alerts: Mapped[list[Alert]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    command: Mapped[str] = mapped_column(String(512))
    raw_output_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    parsed_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    asset: Mapped[Asset] = relationship(back_populates="scans")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    severity: Mapped[str] = mapped_column(String(32), default="low")
    score: Mapped[float] = mapped_column(default=0.0)
    summary: Mapped[str] = mapped_column(String(512))
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")

    asset: Mapped[Optional[Asset]] = relationship(back_populates="alerts")
    actions: Mapped[list[ActionLog]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"))
    action_type: Mapped[str] = mapped_column(String(64))
    executed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    alert: Mapped[Alert] = relationship(back_populates="actions")
