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
   - To require an API key for backend access, set `API_KEY` in `.env` and also set `VITE_API_KEY` so the frontend can send the header.
   - To seed sample data on startup (useful for the dashboard), set `SEED_SAMPLE_DATA=true`.
   - To switch Postgres drivers, set `POSTGRES_DRIVER` (default: `psycopg`).
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

📡 API Execution Flow (Step-by-Step)

Follow these commands in order for a complete DLMS workflow.

🔹 1. List Available Meter Templates
curl.exe http://localhost:8000/emulators/templates

🔹 2. Create a Virtual Meter Instance
curl.exe -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"


⚠️ Save the returned meter_id for next steps.

🔹 3. List All Running Meter Instances
curl.exe http://localhost:8000/emulators/instances

🔹 4. Generate DLMS Fingerprint
curl.exe -X POST http://localhost:8000/fingerprints/<meter_id>

🔹 5. Create Meter Profile
curl.exe -X POST http://localhost:8000/profiles/<meter_id>

🔹 6. Perform DLMS Association (AARQ / AARE)
curl.exe -X POST http://localhost:8000/associations/<meter_id>

🔹 7. Extract Association Object List
curl.exe http://localhost:8000/associations/objects/<meter_id>

🔹 8. Normalize OBIS Codes
curl.exe http://localhost:8000/obis/normalize/<meter_id>

🔹 9. Classify Vendor
curl.exe http://localhost:8000/vendors/classify/<meter_id>

## Project Structure

```
backend/   FastAPI services, discovery logic, data models
frontend/  React dashboard
infra/     Nginx reverse-proxy configuration
```

## License

MIT

## 👨‍💻 Author

Vrushali A Poojary

Software Engineering | AIML | DLMS/COSEM 