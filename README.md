# Software-Defined Universal DLMS Auto-Discovery & Fingerprinting Platform

This repository contains a software-only DLMS/COSEM auto-discovery, emulator, and fingerprinting platform. It provides:

- Virtual DLMS meter emulators with vendor templates.
- Network discovery and authentication negotiation workflows.
- OBIS object extraction and normalization.
- Vendor fingerprinting and classification.
- REST APIs for integration with HES/MDMS systems.
- A React dashboard for discovery operations and meter profiling.

## Architecture Overview

```
frontend (React/Vite)
   |
   |  HTTP (JSON)
   v
backend (FastAPI)
   |
   +-- PostgreSQL (meter profiles/configs)
   +-- MongoDB (fingerprint logs)
```

## Quick Start (Docker)

1. Ensure Docker and Docker Compose are installed.
2. Copy environment defaults and update credentials if needed:
   ```bash
   cp .env.example .env
   ```
3. Start the stack:
   ```bash
   docker compose up --build
   ```
4. Open the UI at `http://localhost:5173`.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend stores **meter profiles** in PostgreSQL (table: `meter_profiles`) and **fingerprints** in MongoDB (`fingerprints` collection). If databases are unavailable, it falls back to in-memory storage.

If `API_KEY` is set in the environment, the API requires the `X-API-Key` header on every request.

To enable real DLMS protocol operations (AARQ/AARE, OBIS extraction), set `DLMS_ADAPTER_URL` to a Gurux/OpenMUC adapter service that exposes:
- `POST /associate` (returns `status`, `authentication`, `security_suite`, `aarq`, `aare`)
- `POST /obis` (returns `normalized` OBIS mappings)
- `GET /health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

The backend exposes OpenAPI/Swagger docs at `http://localhost:8000/docs`.


## API Walkthrough (Quick Demo)

1. List emulator templates:
   ```bash
   curl http://localhost:8000/emulators/templates
   ```
2. Create a virtual meter instance:
   ```bash
   curl -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"
   ```
3. Scan an IP range (bulk scan with port probing):
   ```bash
   curl -X POST http://localhost:8000/discovery/scan \
     -H "Content-Type: application/json" \
     -d '{"ip_range":"127.0.0.0/30","ports":[4059],"max_concurrency":50}'
   ```
4. Review discovery logs:
   ```bash
   curl http://localhost:8000/discovery/logs
   ```
5. Run association handshake (simulated AARQ/AARE):
   ```bash
   curl -X POST http://localhost:8000/associations/<meter_id>
   ```
6. Normalize OBIS mapping:
   ```bash
   curl http://localhost:8000/obis/normalize/<meter_id>
   ```
7. Check DLMS adapter health (if configured):
   ```bash
   curl http://localhost:8000/dlms/adapter/health
   ```
8. Classify vendor:
   ```bash
   curl http://localhost:8000/vendors/classify/<meter_id>
   ```
9. Generate fingerprint:
   ```bash
   curl -X POST http://localhost:8000/fingerprints/<meter_id>
   ```
10. Generate meter profile:
   ```bash
   curl -X POST http://localhost:8000/profiles/<meter_id>
   ```


## Project Structure

```
backend/   FastAPI services, discovery logic, data models
frontend/  React dashboard
infra/     Nginx reverse-proxy configuration
```

## License

MIT
