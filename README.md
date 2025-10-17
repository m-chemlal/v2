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

## 🚀 Getting Started

1. **Clone and configure**
   ```bash
   git clone <repo>
   cd v2
   cp .env.example .env  # adjust targets, credentials if needed
   ```

2. **Launch the platform**
   ```bash
   docker compose up -d --build
   ```

3. **Access the dashboard**
   - Frontend UI: http://localhost:5173
   - API docs: http://localhost:8000/docs

4. **Inspect shared artifacts**
   - Scan outputs: `./data/scans`
   - AI alerts: `./data/alerts/alerts.jsonl`
   - Audit trails: `./data/audit`

Use the provided `Makefile` for common developer shortcuts (`make up`, `make logs`, `make down`).

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
