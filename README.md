# Software-Defined Universal DLMS Auto-Discovery & Fingerprinting Platform

This project is a full-stack DLMS/COSEM demo platform with:
- A FastAPI backend for meter emulation, discovery workflows, associations, OBIS normalization, fingerprinting, and profile generation.
- A React/Vite frontend dashboard that reads backend summary data.
- PostgreSQL storage for generated meter profiles.
- MongoDB storage for fingerprint and discovery logs.

## 1) Project explanation (what it does)

The platform is designed as a software-defined DLMS lab so you can demonstrate complete utility workflows without depending only on physical meters.

### High-level architecture

```text
frontend (React + Vite)
   |
   | HTTP/JSON
   v
backend (FastAPI)
   |
   +-- PostgreSQL (meter_profiles)
   +-- MongoDB (fingerprints, discovery_logs)
```

### Core directories
- `backend/` – API app, business logic, and persistence adapters.
- `frontend/` – dashboard UI.
- `infra/` – nginx reverse proxy config.
- `docker-compose.yml` – local full-stack orchestration.

## 2) Backend workflow (module-by-module)

### Emulator and templates
- Backend seeds built-in meter templates at startup.
- You can create virtual meter instances from templates.
- Endpoints:
  - `GET /emulators/templates`
  - `POST /emulators/templates`
  - `POST /emulators/instances`
  - `POST /emulators/instances/bulk`
  - `GET /emulators/instances`

### Discovery
- `POST /discovery/scan` scans IP range/targets.
- `GET /discovery/logs` returns discovery logs.

### Fingerprinting
- `POST /fingerprints/{meter_id}` generates and stores fingerprint.
- `GET /fingerprints` lists fingerprints.

### Profiles
- `POST /profiles/{meter_id}` generates and stores profile in PostgreSQL.
- `GET /profiles` lists profiles.
- `GET /profiles/{meter_id}/export` exports versioned profile payload.

### DLMS protocol simulation/integration
- `POST /associations/{meter_id}` returns association report.
- `GET /associations/objects/{meter_id}` returns association object list.
- `GET /obis/normalize/{meter_id}` returns normalized OBIS mapping.
- `GET /dlms/adapter/health` checks adapter status.
- `GET /vendors/classify/{meter_id}` classifies vendor.

## 3) Environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Important variables:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `POSTGRES_DRIVER` (default `psycopg`)
- `MONGO_URL`, `MONGO_DB`
- `API_KEY` (optional; when set, backend requires `X-API-Key`)
- `VITE_API_URL` (frontend backend URL, default `http://localhost:8000`)
- `VITE_API_KEY` (optional; frontend sends this as `X-API-Key`)
- `SEED_SAMPLE_DATA` (`true/false`; seeds demo instances/fingerprints/profiles on backend startup)
- `DLMS_ADAPTER_URL` (optional external adapter for real protocol operations)

## 4) Run neatly with Docker (recommended)

1. Prepare env file:
   ```bash
   cp .env.example .env
   ```
2. Demo-friendly `.env` values:
   - `API_KEY=` (empty for easy local demo)
   - `SEED_SAMPLE_DATA=true`
3. Start all services:
   ```bash
   make up
   ```

Equivalent command:
```bash
docker compose up --build
```

Open:
- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- Nginx entrypoint: `http://localhost:8080`

Useful commands:
```bash
make ps
make logs
make down
```

## 5) Run locally without Docker

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If you run backend outside Docker, use local DB host values (example):
- `POSTGRES_HOST=localhost`
- `MONGO_URL=mongodb://localhost:27017`

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## 6) Clean end-to-end workflow (recommended demo order)

1. Start stack (`make up`).
2. Verify backend health and summary:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/summary
   ```
3. Create one virtual meter instance:
   ```bash
   curl -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"
   ```
4. Copy `meter_id`, then run full workflow:
   ```bash
   curl -X POST "http://localhost:8000/fingerprints/<METER_ID>"
   curl -X POST "http://localhost:8000/profiles/<METER_ID>"
   curl -X POST "http://localhost:8000/associations/<METER_ID>"
   curl "http://localhost:8000/associations/objects/<METER_ID>"
   curl "http://localhost:8000/obis/normalize/<METER_ID>"
   curl "http://localhost:8000/vendors/classify/<METER_ID>"
   ```
5. Optional discovery run:
   ```bash
   curl -X POST "http://localhost:8000/discovery/scan" \
     -H "Content-Type: application/json" \
     -d '{"ip_range":"127.0.0.0/30","ports":[4059],"timeout_ms":500,"max_concurrency":20,"retries":0}'
   ```

## 7) DB verification (proof that data is stored)

### PostgreSQL (`meter_profiles`)
```bash
docker compose exec postgres psql -U dlms -d dlms -c "SELECT profile_id,meter_id,vendor,model,created_at FROM meter_profiles ORDER BY created_at DESC LIMIT 10;"
```

### MongoDB (`fingerprints`, `discovery_logs`)
```bash
docker compose exec mongo mongosh --eval "use dlms; db.fingerprints.find({}, {_id:0}).limit(5).pretty(); db.discovery_logs.find({}, {_id:0}).limit(5).pretty();"
```

## 8) API usage notes (Windows PowerShell)

In PowerShell, `curl` maps to `Invoke-WebRequest` and may not accept Linux-style flags like `-X -H -d`.

Use either:
- `curl.exe ...`
- PowerShell cmdlets (`Invoke-RestMethod` / `Invoke-WebRequest`) with PowerShell syntax.

If `API_KEY` is enabled, add:
```bash
-H "X-API-Key: <your_key>"
```

## 9) Troubleshooting checklist

- Frontend loads but no data:
  - Check `VITE_API_URL` points to backend.
  - If `API_KEY` is set, also set `VITE_API_KEY`.
- `meter_not_found` errors:
  - Create an instance first and use its actual `meter_id`.
- Discovery returns reachable but unknown endpoint:
  - This can happen when host:port is reachable but not mapped to a created emulator instance.
- Backend starts but DB data missing:
  - Verify Postgres/Mongo containers are healthy and env vars are correct.

## 10) Recent improvements (SRS alignment uplift)

- **Template management API**: `POST /emulators/templates`
- **Bulk instance provisioning**: `POST /emulators/instances/bulk`
- **Summary endpoint**: `GET /summary`
- **Profile export endpoint**: `GET /profiles/{meter_id}/export`
- **Improved API errors** for missing meters/profiles (`404` behavior)


## 11) Configure and run real DLMS adapter (`DLMS_ADAPTER_URL`) — step by step

This project can run in two modes:
- **Simulation mode** (default): backend generates simulated handshake/object results.
- **Adapter mode**: backend forwards protocol operations to an external DLMS adapter service.

### What URL to use
Set `DLMS_ADAPTER_URL` to the adapter base URL that exposes these endpoints:
- `GET /health`
- `POST /associate`
- `POST /association-objects`
- `POST /obis`

Example values:
- Adapter running on your host: `DLMS_ADAPTER_URL=http://host.docker.internal:9000`
- Adapter running as another compose service: `DLMS_ADAPTER_URL=http://dlms-adapter:9000`
- Adapter running remotely: `DLMS_ADAPTER_URL=https://adapter.example.com`

### Exact steps
1. **Run your adapter service** so it listens on a reachable host/port (for example `0.0.0.0:9000`).
2. **Check adapter health directly**:
   ```bash
   curl http://localhost:9000/health
   ```
3. **Open project env**:
   ```bash
   cp .env.example .env
   ```
4. **Set adapter URL in `.env`**:
   ```dotenv
   DLMS_ADAPTER_URL=http://host.docker.internal:9000
   ```
5. **Restart stack so backend picks new env**:
   ```bash
   make down
   make up
   ```
6. **Confirm backend can see adapter**:
   ```bash
   curl http://localhost:8000/dlms/adapter/health
   ```
7. **Create one meter instance**:
   ```bash
   curl -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"
   ```
8. **Run adapter-backed protocol endpoints** (replace `<METER_ID>`):
   ```bash
   curl -X POST "http://localhost:8000/associations/<METER_ID>"
   curl "http://localhost:8000/associations/objects/<METER_ID>"
   curl "http://localhost:8000/obis/normalize/<METER_ID>"
   ```
9. **Verify response is adapter-driven** by checking fields/content expected from your adapter.
10. **If auth is enabled**, include API key in every backend call:
    ```bash
    curl -H "X-API-Key: <your_key>" http://localhost:8000/dlms/adapter/health
    ```

### Troubleshooting adapter connectivity
- `{"status":"disabled"}` from `/dlms/adapter/health`:
  - `DLMS_ADAPTER_URL` is empty or not loaded; restart backend.
- Connection timeout/refused:
  - adapter not running, wrong port, or not bound to `0.0.0.0`.
- Using Docker and adapter on host machine:
  - prefer `host.docker.internal` instead of `localhost`.
- TLS adapters:
  - use `https://...` URL and ensure cert chain is valid from backend container.

## License
MIT

## 👨‍💻 Author
Vrushali A Poojary

Software Engineering | AIML | DLMS/COSEM
