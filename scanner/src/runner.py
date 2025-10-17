from __future__ import annotations

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import xmltodict
from loguru import logger

DATA_DIR = Path(os.getenv("SCAN_DATA_DIR", "/data/scans"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
SCAN_TARGETS = os.getenv("SCAN_TARGETS", "192.168.1.0/24")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "900"))
NMAP_BINARY = os.getenv("NMAP_BINARY", "nmap")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_nmap_scan(output_file: Path) -> None:
    command = [
        NMAP_BINARY,
        "-sV",
        "-O",
        "-Pn",
        SCAN_TARGETS,
        "-oX",
        str(output_file),
    ]
    logger.info("Running Nmap command: {}", " ".join(command))
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        logger.warning("Nmap binary not found. Generating demo scan output instead.")
        output_file.write_text(
            """
<nmaprun>
  <host>
    <address addr='192.168.1.10' addrtype='ipv4'/>
    <ports>
      <port protocol='tcp' portid='22'>
        <state state='open'/>
        <service name='ssh' method='table'/>
      </port>
      <port protocol='tcp' portid='80'>
        <state state='open'/>
        <service name='http' method='table'/>
      </port>
    </ports>
  </host>
</nmaprun>
"""
        )
    except subprocess.CalledProcessError as exc:
        logger.error("Nmap failed: {}", exc)
        if not output_file.exists():
            output_file.write_text("""<nmaprun></nmaprun>""")


def parse_scan_xml(xml_path: Path) -> dict[str, Any]:
    if not xml_path.exists():
        return {}
    try:
        xml_content = xml_path.read_text()
        parsed = xmltodict.parse(xml_content)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to parse Nmap XML: {}", exc)
        return {}

    hosts = parsed.get("nmaprun", {}).get("host", [])
    if isinstance(hosts, dict):
        hosts = [hosts]

    results: list[dict[str, Any]] = []
    for host in hosts:
        address = host.get("address", {})
        if isinstance(address, list):
            address = address[0]
        ip = address.get("@addr", "unknown")
        ports_info = host.get("ports", {}).get("port", [])
        if isinstance(ports_info, dict):
            ports_info = [ports_info]
        ports: list[dict[str, Any]] = []
        for port in ports_info:
            ports.append(
                {
                    "port": int(port.get("@portid", 0)),
                    "protocol": port.get("@protocol", "tcp"),
                    "state": port.get("state", {}).get("@state", "unknown"),
                    "service": port.get("service", {}).get("@name", "unknown"),
                }
            )
        results.append({"ip": ip, "ports": ports})
    return {"generated_at": datetime.utcnow().isoformat(), "hosts": results}


async def post_scan_to_backend(payload: dict[str, Any]) -> None:
    async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=30) as client:
        for host in payload.get("hosts", []):
            hostname = host.get("hostname", "auto-discovered")
            ip_address = host.get("ip", "0.0.0.0")
            asset_response = await client.post(
                "/api/v1/assets",
                json={"hostname": hostname, "ip_address": ip_address, "os": "unknown"},
            )
            try:
                asset_response.raise_for_status()
                asset_id = asset_response.json().get("id")
            except (httpx.HTTPStatusError, ValueError):
                logger.error("Failed to create asset for %s", ip_address)
                continue
            scan_response = await client.post(
                "/api/v1/scans",
                json={
                    "asset_id": asset_id,
                    "command": f"nmap {SCAN_TARGETS}",
                    "parsed_result": host,
                },
            )
            logger.info(
                "Reported scan for %s -> status=%s", ip_address, scan_response.status_code
            )


async def scan_loop() -> None:
    ensure_data_dir()
    while True:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        output_file = DATA_DIR / f"scan_{timestamp}.xml"
        run_nmap_scan(output_file)
        parsed = parse_scan_xml(output_file)
        (DATA_DIR / f"scan_{timestamp}.json").write_text(json.dumps(parsed, indent=2))
        await post_scan_to_backend(parsed)
        await asyncio.sleep(SCAN_INTERVAL)


def main() -> None:
    try:
        asyncio.run(scan_loop())
    except KeyboardInterrupt:
        logger.info("Scanner stopped")


if __name__ == "__main__":
    main()
