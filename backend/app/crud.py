from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def init_models(session: AsyncSession) -> None:
    async with session.bind.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def upsert_asset(session: AsyncSession, asset: schemas.AssetCreate) -> models.Asset:
    result = await session.execute(
        select(models.Asset).where(models.Asset.ip_address == asset.ip_address)
    )
    db_asset = result.scalar_one_or_none()
    if db_asset is None:
        db_asset = models.Asset(
            hostname=asset.hostname,
            ip_address=asset.ip_address,
            os=asset.os,
            last_seen=datetime.utcnow(),
        )
        session.add(db_asset)
    else:
        db_asset.hostname = asset.hostname
        db_asset.os = asset.os
        db_asset.last_seen = datetime.utcnow()
    await session.commit()
    await session.refresh(db_asset)
    return db_asset


async def create_scan(session: AsyncSession, scan: schemas.ScanCreate) -> models.Scan:
    db_scan = models.Scan(**scan.model_dump())
    session.add(db_scan)
    await session.commit()
    await session.refresh(db_scan)
    return db_scan


async def create_alert(session: AsyncSession, alert: schemas.AlertCreate) -> models.Alert:
    db_alert = models.Alert(**alert.model_dump())
    session.add(db_alert)
    await session.commit()
    await session.refresh(db_alert)
    return db_alert


async def list_alerts(session: AsyncSession, limit: int = 20) -> Sequence[models.Alert]:
    result = await session.execute(
        select(models.Alert).order_by(models.Alert.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


async def list_scans(session: AsyncSession, limit: int = 20) -> Sequence[models.Scan]:
    result = await session.execute(select(models.Scan).order_by(models.Scan.id.desc()).limit(limit))
    return result.scalars().all()


async def create_action_log(
    session: AsyncSession, action_log: schemas.ActionLogCreate
) -> models.ActionLog:
    db_action = models.ActionLog(**action_log.model_dump())
    session.add(db_action)
    await session.commit()
    await session.refresh(db_action)
    return db_action


async def get_dashboard_summary(session: AsyncSession) -> schemas.DashboardSummary:
    alerts_result = await session.execute(select(func.count()).select_from(models.Alert))
    total_alerts = alerts_result.scalar_one() or 0

    severity_counts = await session.execute(
        select(models.Alert.severity, func.count(models.Alert.id)).group_by(models.Alert.severity)
    )
    counts = {severity: count for severity, count in severity_counts}

    latest_alerts = await session.execute(
        select(models.Alert).order_by(models.Alert.created_at.desc()).limit(5)
    )
    recent_scans = await session.execute(
        select(models.Scan).order_by(models.Scan.started_at.desc()).limit(5)
    )
    recent_actions = await session.execute(
        select(models.ActionLog).order_by(models.ActionLog.executed_at.desc()).limit(5)
    )

    high = counts.get("high", 0)
    medium = counts.get("medium", 0)
    low = counts.get("low", 0)

    ai_insights = {
        "top_signals": ["exposed_ssh", "anonymous_ftp"],
        "model_version": "0.1.0",
    }

    return schemas.DashboardSummary(
        vulnerabilities_detected=total_alerts,
        high_count=high,
        medium_count=medium,
        low_count=low,
        ai_insights=ai_insights,
        recent_scans=[schemas.ScanRead.model_validate(scan) for scan in recent_scans.scalars().all()],
        latest_alerts=[schemas.AlertRead.model_validate(alert) for alert in latest_alerts.scalars().all()],
        automated_actions=[schemas.ActionLogRead.model_validate(action) for action in recent_actions.scalars().all()],
    )
