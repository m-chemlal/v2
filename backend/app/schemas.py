from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    total: int
    limit: int = 50
    offset: int = 0


class AssetBase(BaseModel):
    hostname: str
    ip_address: str
    os: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetRead(AssetBase):
    id: int
    last_seen: datetime

    class Config:
        from_attributes = True


class ScanBase(BaseModel):
    asset_id: int
    command: str
    raw_output_path: Optional[str] = None
    parsed_result: Optional[dict[str, Any]] = None


class ScanCreate(ScanBase):
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class ScanRead(ScanBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    asset_id: Optional[int]
    severity: str = "low"
    score: float = 0.0
    summary: str
    details: Optional[dict[str, Any]] = None
    explanation: Optional[dict[str, Any]] = None
    status: str = "open"


class AlertCreate(AlertBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AlertRead(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionLogBase(BaseModel):
    alert_id: int
    action_type: str
    details: Optional[dict[str, Any]] = None


class ActionLogCreate(ActionLogBase):
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class ActionLogRead(ActionLogBase):
    id: int
    executed_at: datetime

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    vulnerabilities_detected: int
    high_count: int
    medium_count: int
    low_count: int
    ai_insights: dict[str, Any]
    recent_scans: list[ScanRead]
    latest_alerts: list[AlertRead]
    automated_actions: list[ActionLogRead]
