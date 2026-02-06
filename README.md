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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

The backend exposes OpenAPI/Swagger docs at `http://localhost:8000/docs`.

## Project Structure

```
backend/   FastAPI services, discovery logic, data models
frontend/  React dashboard
infra/     Nginx reverse-proxy configuration
```

## License

MIT
