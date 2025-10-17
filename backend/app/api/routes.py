from __future__ import annotations

from fastapi import APIRouter, Depends, status

from .. import crud, schemas
from ..database import get_session

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/assets", response_model=schemas.AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: schemas.AssetCreate,
    session=Depends(get_session),
) -> schemas.AssetRead:
    db_asset = await crud.upsert_asset(session, asset)
    return schemas.AssetRead.model_validate(db_asset)


@router.get("/alerts", response_model=list[schemas.AlertRead])
async def get_alerts(session=Depends(get_session)) -> list[schemas.AlertRead]:
    alerts = await crud.list_alerts(session)
    return [schemas.AlertRead.model_validate(alert) for alert in alerts]


@router.post("/alerts", response_model=schemas.AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: schemas.AlertCreate,
    session=Depends(get_session),
) -> schemas.AlertRead:
    db_alert = await crud.create_alert(session, alert)
    return schemas.AlertRead.model_validate(db_alert)


@router.post("/scans", response_model=schemas.ScanRead, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan: schemas.ScanCreate,
    session=Depends(get_session),
) -> schemas.ScanRead:
    db_scan = await crud.create_scan(session, scan)
    return schemas.ScanRead.model_validate(db_scan)


@router.get("/scans", response_model=list[schemas.ScanRead])
async def get_scans(session=Depends(get_session)) -> list[schemas.ScanRead]:
    scans = await crud.list_scans(session)
    return [schemas.ScanRead.model_validate(scan) for scan in scans]


@router.post("/actions", response_model=schemas.ActionLogRead, status_code=status.HTTP_201_CREATED)
async def create_action(
    action: schemas.ActionLogCreate,
    session=Depends(get_session),
) -> schemas.ActionLogRead:
    db_action = await crud.create_action_log(session, action)
    return schemas.ActionLogRead.model_validate(db_action)


@router.get("/dashboard", response_model=schemas.DashboardSummary)
async def get_dashboard(session=Depends(get_session)) -> schemas.DashboardSummary:
    summary = await crud.get_dashboard_summary(session)
    return summary
