from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
MODEL_REFRESH_INTERVAL = int(os.getenv("MODEL_REFRESH_INTERVAL", "600"))
ALERTS_DIR = Path(os.getenv("ALERTS_DIR", "/data/alerts"))
AUDIT_DIR = Path(os.getenv("AUDIT_DIR", "/data/audit"))


def ensure_directories() -> None:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def compute_risk_score(parsed_result: dict[str, Any]) -> tuple[float, str, list[dict[str, Any]]]:
    ports = parsed_result.get("ports", [])
    open_ports = [p for p in ports if p.get("state") == "open"]
    high_risk_ports = {22, 3389, 445, 5900, 21, 23}

    feature_importance: list[dict[str, Any]] = []
    score = 0.1 * len(open_ports)
    if any(port.get("port") in high_risk_ports for port in open_ports):
        score += 0.4
        feature_importance.append({"feature": "high_risk_port", "value": 1, "impact": 0.4})
    if len(open_ports) > 5:
        score += 0.2
        feature_importance.append({"feature": "too_many_open_ports", "value": len(open_ports), "impact": 0.2})
    if len(open_ports) == 0:
        score = 0.05
        feature_importance.append({"feature": "no_open_ports", "value": 0, "impact": -0.1})

    score = min(score, 1.0)

    severity = "low"
    if score >= 0.7:
        severity = "high"
    elif score >= 0.4:
        severity = "medium"

    if not feature_importance:
        feature_importance.append({"feature": "baseline", "value": 1, "impact": score})

    return score, severity, feature_importance


async def fetch_scans(client: httpx.AsyncClient) -> Sequence[dict[str, Any]]:
    response = await client.get("/api/v1/scans")
    response.raise_for_status()
    return response.json()


async def fetch_existing_alerts(client: httpx.AsyncClient) -> Sequence[dict[str, Any]]:
    response = await client.get("/api/v1/alerts")
    response.raise_for_status()
    return response.json()


def alert_exists(existing_alerts: Sequence[dict[str, Any]], asset_id: int, summary: str) -> bool:
    return any((alert.get("asset_id") == asset_id) and (alert.get("summary") == summary) for alert in existing_alerts)


async def emit_alert(
    client: httpx.AsyncClient,
    asset_id: int,
    summary: str,
    severity: str,
    score: float,
    parsed_result: dict[str, Any],
    feature_importance: list[dict[str, Any]],
) -> dict[str, Any]:
    alert_payload = {
        "asset_id": asset_id,
        "summary": summary,
        "severity": severity,
        "score": round(score, 2),
        "details": parsed_result,
        "explanation": {"feature_importance": feature_importance},
    }
    response = await client.post("/api/v1/alerts", json=alert_payload)
    response.raise_for_status()
    alert_record = response.json()

    alert_path = ALERTS_DIR / "alerts.jsonl"
    with alert_path.open("a", encoding="utf-8") as alert_file:
        alert_file.write(json.dumps(alert_record) + "\n")

    audit_path = AUDIT_DIR / "audit.jsonl"
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "alert_created",
        "alert_id": alert_record["id"],
        "score": score,
        "severity": severity,
        "summary": summary,
        "explanation": feature_importance,
    }
    with audit_path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(audit_entry) + "\n")

    logger.info("AI engine emitted alert %s severity=%s score=%.2f", alert_record["id"], severity, score)


async def process_scans() -> None:
    ensure_directories()
    async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=30) as client:
        scans = await fetch_scans(client)
        existing_alerts = await fetch_existing_alerts(client)

        for scan in scans:
            asset_id = scan.get("asset_id")
            parsed_result = scan.get("parsed_result") or {}
            if asset_id is None or not parsed_result:
                continue
            summary = f"AI risk score for asset {asset_id}"
            if alert_exists(existing_alerts, asset_id, summary):
                logger.debug("Alert already exists for asset %s", asset_id)
                continue
            score, severity, feature_importance = compute_risk_score(parsed_result)
            alert_record = await emit_alert(
                client,
                asset_id=asset_id,
                summary=summary,
                severity=severity,
                score=score,
                parsed_result=parsed_result,
                feature_importance=feature_importance,
            )
            existing_alerts = [*existing_alerts, alert_record]


async def worker_loop() -> None:
    while True:
        try:
            await process_scans()
        except httpx.HTTPError as exc:
            logger.error("Failed to process scans: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error in AI engine: %s", exc)
        await asyncio.sleep(MODEL_REFRESH_INTERVAL)


def main() -> None:
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("AI engine stopped")


if __name__ == "__main__":
    main()
