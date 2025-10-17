# TRUSTED AI SOC LITE

Prototype architecture for a local, explainable Security Operations Center built around automated scanning, AI enrichment, and autonomous response. This stack is designed for a single Debian host using Docker Compose.

## 📦 Stack Overview

| Service | Purpose |
| --- | --- |
| `postgres` | Stores assets, scans, alerts, and audit trails. |
| `backend` | FastAPI service that exposes REST endpoints and persists data. |
| `scanner` | Nmap-based discovery agent that publishes raw/parsed scan results. |
| `ai-engine` | Scores findings, generates SHAP-style explanations, and writes audit logs. |
| `responder` | Applies playbooks (block/email/log) and appends to audit trails. |
| `frontend` | React + Tailwind dashboard inspired by the TRUSTED AI SOC LITE mockup. |

All services communicate on the isolated `soc-net` Docker network and share structured artifacts via the `shared-data` volume (`/data` inside containers).

## 🚀 Getting Started (Step by Step)

### 0. Prerequisites

- Debian (or any Linux/macOS host) with **Docker** and **Docker Compose plugin** installed
  ```bash
  sudo apt update && sudo apt install docker.io docker-compose-plugin make
  sudo usermod -aG docker $USER   # log out/in afterwards
  ```
- Optional but recommended: **Make** (invoked in the commands below)

### 1. Clone the repository and prepare environment variables

```bash
git clone <repo>
cd v2
cp .env.example .env
# edit .env to set POSTGRES password, scan ranges (SCAN_TARGETS), etc.
```

### 2. Build and launch all services

```bash
make up        # equivalent to: docker compose up -d --build
make logs      # follow logs until each service reports "Started" status
```

The first build can take several minutes while Docker pulls base images and installs dependencies.

### 3. Verify that core services are reachable

- Backend health check: http://localhost:8000/docs should load the FastAPI Swagger UI.
- Frontend dashboard: http://localhost:5173 should render seeded demo data.
- Database check (optional): `docker compose exec postgres psql -U soc -d soc`.

### 4. Trigger a manual scan + AI run (end-to-end data path)

```bash
make scan      # runs nmap once and pushes results to the backend
make ai        # processes the latest scans, produces alerts & explanations
```

Artifacts land under the `./data` directory on the host (because of the shared volume):

- `./data/scans/` – raw XML and parsed JSON from the scanner
- `./data/alerts/alerts.jsonl` – AI alerts with scores and XAI factors
- `./data/audit/` – responder audit trails

### 5. Exercise the automated responder

By default the responder tails `alerts.jsonl`. To simulate a high-risk alert without waiting for a real scan:

```bash
make demo      # invokes the AI engine to emit a synthetic critical alert
```

Observe the new responder action in the dashboard **Actions** panel and confirm an entry appended to `./data/audit/responses.jsonl`.

### 6. Interact with the API directly (optional)

Use `curl` or any REST client against `http://localhost:8000/api/v1`:

```bash
# List recent alerts
curl http://localhost:8000/api/v1/alerts

# Create a manual response record
curl -X POST http://localhost:8000/api/v1/actions \
  -H 'Content-Type: application/json' \
  -d '{"alert_id": 1, "action": "notified_team", "details": "Called on-call analyst"}'
```

### 7. Shut the stack down when finished

```bash
make down      # or: docker compose down
```

Add `make clean` if you also want to remove shared artifacts under `./data`.

## 🧠 Data Flow

```
scanner (Nmap) ──▶ backend (FastAPI + Postgres)
                         │
                         ▼
ai-engine (risk scoring + XAI) ──▶ alerts.jsonl / audit.jsonl ──▶ responder
                         │
                         └────▶ REST API consumed by React dashboard
```

- The **scanner** normalizes Nmap XML into JSON and posts both the asset and scan payloads to the backend.
- The **AI engine** reads recent scans, computes heuristic risk scores, emits explainable alerts, and persists JSONL audit logs.
- The **responder** tails generated alerts and simulates playbooks (e.g., blocking an IP or sending an email) while recording responses back into the backend.
- The **frontend** polls `/api/v1/dashboard` to render metrics, alerts, scans, AI insights, and action history in real time.

## 🔧 Customisation Tips

- Update `SCAN_TARGETS` (comma-separated CIDR list) in `.env` to match your lab network.
- Extend the AI heuristics in `ai_engine/src/worker.py` with scikit-learn models or SHAP values.
- Define real playbooks in `responder/src/responder.py` (e.g., UFW commands, SMTP notifications).
- Tailor the dashboard styling/components under `frontend/src/` to match your SOC branding.

## 🛡️ Security Considerations

- Keep Docker services on a private network; only expose the UI (5173) and API (8000) externally if required.
- Provide strong credentials for Postgres (`POSTGRES_PASSWORD`) before any production usage.
- Implement TLS termination for the frontend/backend via a reverse proxy (Traefik, Caddy, Nginx) when publishing outside localhost.

## 📚 API Glimpse

Key REST resources (all under `/api/v1/`):

- `POST /assets` – Upsert asset metadata from discovery.
- `POST /scans` / `GET /scans` – Store and list scan runs.
- `POST /alerts` / `GET /alerts` – Persist AI-generated alerts and fetch recent ones.
- `POST /actions` – Audit responder actions.
- `GET /dashboard` – Aggregated snapshot consumed by the React UI.

Explore full schemas through the interactive Swagger UI at `/docs` once the stack is running.

## 🧪 Demo Data

On startup, the backend seeds a demo asset, scan, alert, and response to make the dashboard informative even before real scans execute. Replace or disable this seeding logic in `backend/app/main.py` for production deployments.

## 🗺️ Next Steps

- Integrate additional scanners (OpenVAS, custom scripts).
- Plug in a threat intelligence feed and enrich alerts with context.
- Swap SQLite-compatible storage for high-availability Postgres, or stream events into Kafka/Redis for scale.
- Expand responder playbooks to interact with firewalls, ticketing systems, or SOAR platforms.

Happy hacking! 🚀
