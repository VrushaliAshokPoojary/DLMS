# Software-Defined Universal DLMS Auto-Discovery & Fingerprinting Platform

This project is a full-stack DLMS/COSEM demo platform with:
- A FastAPI backend for meter emulation, discovery workflows, associations, OBIS normalization, fingerprinting, and profile generation.
- A React/Vite frontend dashboard that reads backend summary data.
- PostgreSQL storage for generated meter profiles.
- MongoDB storage for fingerprint and discovery logs.

## 1) How the project is organized

```
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
- `backend/` – API app, business logic, DB persistence adapters.
- `frontend/` – dashboard UI.
- `infra/` – nginx reverse proxy config.
- `docker-compose.yml` – local full-stack orchestration.

## 2) Backend behavior (what each module does)

### Emulator and templates
- The backend seeds built-in meter templates at startup.
- You can create virtual meter instances from templates.
- Endpoints:
  - `GET /emulators/templates`
  - `POST /emulators/instances`
  - `GET /emulators/instances`

### Discovery
- `POST /discovery/scan` returns discovered results.
- `GET /discovery/logs` returns discovery log documents from MongoDB (if available).

### Fingerprinting
- `POST /fingerprints/{meter_id}` generates and stores a fingerprint.
- `GET /fingerprints` lists stored fingerprints.

### Profiles
- `POST /profiles/{meter_id}` generates and stores a profile in PostgreSQL.
- `GET /profiles` lists profiles.

### DLMS protocol simulation/integration
- `POST /associations/{meter_id}` returns association report.
- `GET /obis/normalize/{meter_id}` returns normalized OBIS mapping.
- `GET /dlms/adapter/health` checks adapter status.
- `GET /vendors/classify/{meter_id}` classifies vendor.

## 3) Environment variables

Copy `.env.example` to `.env` and edit values:

```bash
cp .env.example .env
```

### Important variables
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `POSTGRES_DRIVER` (default `psycopg`)
- `MONGO_URL`, `MONGO_DB`
- `API_KEY` (optional; when set, backend requires `X-API-Key`)
- `VITE_API_URL` (frontend backend URL, default `http://localhost:8000`)
- `VITE_API_KEY` (optional; frontend sends this as `X-API-Key`)
- `SEED_SAMPLE_DATA` (`true/false`; seeds demo instances/fingerprints/profiles on backend startup)
- `DLMS_ADAPTER_URL` (optional external adapter for real protocol operations)

## 4) Run with Docker (recommended)

1. Prepare env file:
   ```bash
   cp .env.example .env
   ```
2. Optional demo-friendly settings in `.env`:
   - `API_KEY=` (empty for easier demo)
   - `SEED_SAMPLE_DATA=true`
3. Start all services:
   ```bash
   make up
   ```
4. Open:
   - Frontend: `http://localhost:5173`
   - Backend docs: `http://localhost:8000/docs`
   - Nginx entrypoint: `http://localhost:8080`

## 5) Run locally without Docker

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 6) API usage notes (especially for Windows PowerShell)

In PowerShell, `curl` maps to `Invoke-WebRequest` and does not accept Linux-style flags like `-X -H -d`.

Use one of these approaches:
- Use the real curl binary: `curl.exe ...`
- Or use PowerShell cmdlets (`Invoke-RestMethod` / `Invoke-WebRequest`) with PowerShell syntax.

### Example commands (cross-platform using `curl.exe`)

1. List templates:
```bash
curl.exe http://localhost:8000/emulators/templates
```

2. Create meter instance:
```bash
curl.exe -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"
```

3. List instances (copy `meter_id`):
```bash
curl.exe http://localhost:8000/emulators/instances
```

4. Generate fingerprint/profile (replace `<METER_ID>`):
```bash
curl.exe -X POST "http://localhost:8000/fingerprints/<METER_ID>"
curl.exe -X POST "http://localhost:8000/profiles/<METER_ID>"
```

5. Check discovery logs:
```bash
curl.exe http://localhost:8000/discovery/logs
```

### If `API_KEY` is enabled
Add header to every request:
```bash
curl.exe -H "X-API-Key: <your_key>" http://localhost:8000/emulators/templates
```

## 7) Data storage details

- PostgreSQL table: `meter_profiles`
- MongoDB collections:
  - `fingerprints`
  - `discovery_logs`

If DB connections fail, the backend falls back to in-memory behavior for some components.

## 8) Typical demo flow

1. Start stack (`docker compose up --build`).
2. Open `/docs` and verify backend health.
3. Create one instance from a template.
4. Generate fingerprint and profile for that meter.
5. Open frontend and show summary cards updating.
6. Optionally inspect DB contents directly via Mongo/Postgres clients.

## 9) Troubleshooting checklist

- Frontend loads but no data:
  - Check `VITE_API_URL` points to backend.
  - If `API_KEY` is set, also set `VITE_API_KEY`.
- `meter_not_found` errors:
  - Create an instance first and use its actual `meter_id`.
- PowerShell errors with `-X/-H/-d`:
  - Use `curl.exe`, not `curl` alias.
- Backend starts but DB data missing:
  - Verify Postgres/Mongo containers are healthy and env vars are correct.

## License

MIT

## 👨‍💻 Author

Vrushali A Poojary

Software Engineering | AIML | DLMS/COSEM 

## 10) Recent improvements (SRS alignment uplift)

The project now includes several concrete upgrades to close key SRS gaps:

- **Template management API**: create new meter templates at runtime.
  - `POST /emulators/templates`
- **Bulk instance provisioning** for large simulation setup.
  - `POST /emulators/instances/bulk`
- **Summary endpoint** for dashboard/integration quick telemetry.
  - `GET /summary`
- **Profile export endpoint** with schema version metadata.
  - `GET /profiles/{meter_id}/export`
- **Improved API errors** for missing meters/profiles (`404` instead of silent error payloads).

### Bulk provisioning example
```bash
curl -X POST "http://localhost:8000/emulators/instances/bulk"   -H "Content-Type: application/json"   -d '{
    "vendor":"Acme Energy",
    "model":"A1000",
    "base_ip":"10.20.0.10",
    "start_port":5000,
    "count":25
  }'
```

### Template creation example
```bash
curl -X POST "http://localhost:8000/emulators/templates"   -H "Content-Type: application/json"   -d '{
    "vendor":"Nova Grid",
    "model":"N200",
    "referencing":"LN",
    "authentication_modes":["LLS","HLS"],
    "security_suites":[1,2],
    "obis_objects":[
      {"code":"1-0:1.8.0","description":"Active energy import","data_type":"double","unit":"kWh"}
    ]
  }'
```

## 11) If you want my assistance to complete remaining tasks

To help finish full SRS compliance quickly, please provide these from your side:

1. **Adapter service access details**
   - Running URL for Gurux/OpenMUC adapter (`DLMS_ADAPTER_URL`), or adapter repo.
2. **Target test profiles**
   - 3-5 vendor/model protocol behavior expectations to validate handshake/object extraction.
3. **Scale test environment budget**
   - Whether we can run long load tests (k6/Locust) and store report artifacts.
4. **Acceptance proof format**
   - Whether your faculty expects PDF report, PPT, or both (I can generate exact structure).

With these inputs, remaining FR/NFR closure can be delivered in a deterministic checklist-driven manner.
