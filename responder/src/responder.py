from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
POLICY_PATH = Path(os.getenv("RESPONSE_POLICY", "/app/policy.json"))
ALERTS_FILE = Path(os.getenv("ALERTS_FILE", "/data/alerts/alerts.jsonl"))
AUDIT_DIR = Path(os.getenv("AUDIT_DIR", "/data/audit"))
STATE_PATH = Path(os.getenv("RESPONDER_STATE", "/app/.responder_state.json"))

DEFAULT_POLICY = {
    "thresholds": {
        "critical": "block_ip",
        "high": "block_ip",
        "medium": "email_only",
        "low": "audit_only",
    },
    "email_recipients": ["soc-ops@example.local"],
}


def load_policy() -> dict[str, Any]:
    if not POLICY_PATH.exists():
        POLICY_PATH.write_text(json.dumps(DEFAULT_POLICY, indent=2), encoding="utf-8")
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def ensure_audit_dir() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


async def apply_action(client: httpx.AsyncClient, alert: dict[str, Any], action: str) -> None:
    audit_path = AUDIT_DIR / "response.jsonl"
    details = {
        "action": action,
        "alert_id": alert.get("id"),
        "target": alert.get("details", {}).get("ip"),
        "timestamp": datetime.utcnow().isoformat(),
    }
    if action == "block_ip":
        logger.info("Simulating firewall block for alert %s", alert.get("id"))
        details["status"] = "blocked"
    elif action == "email_only":
        logger.info("Simulating email notification for alert %s", alert.get("id"))
        details["status"] = "emailed"
    else:
        details["status"] = "logged"

    with audit_path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(details) + "\n")

    if alert.get("id"):
        await client.post(
            "/api/v1/actions",
            json={
                "alert_id": alert["id"],
                "action_type": details["status"],
                "details": details,
            },
        )


def load_state() -> set[int]:
    if not STATE_PATH.exists():
        return set()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return set(data.get("processed_ids", []))
    except json.JSONDecodeError:
        return set()


def save_state(processed_ids: set[int]) -> None:
    STATE_PATH.write_text(json.dumps({"processed_ids": sorted(processed_ids)}), encoding="utf-8")


async def process_alerts(policy: dict[str, Any], processed_ids: set[int]) -> set[int]:
    ensure_audit_dir()
    async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=30) as client:
        if not ALERTS_FILE.exists():
            return processed_ids
        for line in ALERTS_FILE.read_text(encoding="utf-8").splitlines():
            try:
                alert = json.loads(line)
            except json.JSONDecodeError:
                continue
            alert_id = alert.get("id")
            if alert_id is None or alert_id in processed_ids:
                continue
            severity = alert.get("severity", "low")
            action = policy.get("thresholds", {}).get(severity, "audit_only")
            await apply_action(client, alert, action)
            processed_ids.add(alert_id)
    return processed_ids


async def responder_loop() -> None:
    policy = load_policy()
    processed_ids = load_state()
    while True:
        try:
            processed_ids = await process_alerts(policy, processed_ids)
            save_state(processed_ids)
        except httpx.HTTPError as exc:
            logger.error("Responder HTTP error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected responder error: %s", exc)
        await asyncio.sleep(int(os.getenv("RESPONDER_INTERVAL", "120")))


def main() -> None:
    try:
        asyncio.run(responder_loop())
    except KeyboardInterrupt:
        logger.info("Responder stopped")


if __name__ == "__main__":
    main()
