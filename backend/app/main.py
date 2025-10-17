from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import crud, schemas
from .api.routes import router as api_router
from .config import settings
from .database import SessionLocal

app = FastAPI(title="Trusted AI SOC Lite API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def on_startup() -> None:
    async with SessionLocal() as session:
        await crud.init_models(session)

    async with SessionLocal() as session:
        asset = await crud.upsert_asset(
            session,
            asset=schemas.AssetCreate(hostname="demo-host", ip_address="192.168.1.10", os="Debian"),
        )
        scans = await crud.list_scans(session)
        if not scans:
            await crud.create_scan(
                session,
                schemas.ScanCreate(
                    asset_id=asset.id,
                    command="nmap -sV -O 192.168.1.10",
                    raw_output_path="/data/scans/demo.xml",
                    parsed_result={
                        "ports": [
                            {"port": 22, "service": "ssh", "state": "open"},
                            {"port": 443, "service": "https", "state": "open"},
                        ]
                    },
                    started_at=datetime.utcnow() - timedelta(minutes=5),
                    ended_at=datetime.utcnow(),
                ),
            )
        alerts = await crud.list_alerts(session)
        if not alerts:
            alert = await crud.create_alert(
                session,
                schemas.AlertCreate(
                    asset_id=asset.id,
                    severity="high",
                    score=0.92,
                    summary="High-risk SSH exposed on public network",
                    details={"port": 22, "protocol": "tcp", "finding": "ssh"},
                    explanation={
                        "top_features": [
                            {"name": "internet_exposed", "importance": 0.45},
                            {"name": "weak_cipher", "importance": 0.23},
                        ]
                    },
                ),
            )
            await crud.create_action_log(
                session,
                schemas.ActionLogCreate(
                    alert_id=alert.id,
                    action_type="blocked",
                    details={"mechanism": "ufw", "target": "192.168.1.10"},
                ),
            )


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Trusted AI SOC Lite backend is running"}
