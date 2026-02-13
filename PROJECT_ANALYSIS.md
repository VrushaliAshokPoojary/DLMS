# DLMS Project Analysis

## What this project is

This repository is a **software-defined DLMS/COSEM discovery and profiling platform** built as a full-stack application:

- A **FastAPI backend** that simulates and manages DLMS meter instances, runs discovery/fingerprinting/profile workflows, and exposes REST APIs.
- A **React/Vite frontend** that gives operators a control-plane dashboard with summary metrics.
- Optional persistence using **PostgreSQL** (meter profiles) and **MongoDB** (fingerprints and discovery logs), with graceful in-memory fallback.
- Containerized local runtime via Docker Compose.

In short, this is a practical platform for prototyping utility workflows: create virtual meters, discover them, fingerprint/classify vendors, negotiate association parameters, normalize OBIS maps, and produce profile data suitable for HES/MDMS integration.

## System architecture

- **Frontend (`frontend/`)** calls backend APIs over HTTP.
- **Backend (`backend/app/main.py`)** orchestrates domain services.
- **PostgreSQL** stores long-lived profile records (`meter_profiles` table).
- **MongoDB** stores fingerprint logs and discovery scan logs.
- **DLMS adapter integration (optional)** supports plugging in a real protocol service for AARQ/AARE and OBIS extraction.

## Main backend capabilities by module

- `emulator.py`: template registry + virtual meter instance lifecycle.
- `discovery.py`: discovery engine abstraction for scanning/probing and producing `DiscoveryResult`s.
- `fingerprinting.py`: feature extraction and vendor-signature logging.
- `profiles.py`: deterministic profile generation and storage abstraction.
- `association.py`: simulated AARQ/AARE negotiation.
- `obis.py`: OBIS normalization map generation.
- `vendor.py`: basic vendor classification with confidence scores.
- `dlms_client.py`: optional adapter-backed protocol operations.

## API surface (core flows)

1. List templates / create emulated meter instances.
2. Scan discovery targets and inspect discovery logs.
3. Fingerprint a meter and list fingerprint history.
4. Generate profile and list profiles.
5. Run association negotiation.
6. Normalize OBIS codes.
7. Classify vendor.

## Frontend role

The React app is intentionally lightweight and acts as an operations dashboard:

- Fetches summary counts from templates, instances, and profiles endpoints.
- Displays status cards and operational readiness table.
- Reads API base URL/API key from environment variables.

## Core concepts to learn (in recommended order)

1. **DLMS/COSEM fundamentals**
   - What DLMS/COSEM is, client/server model, and meter communication lifecycle.
   - Object model basics and why OBIS is central.

2. **OBIS code semantics and normalization**
   - How raw OBIS codes represent measurements.
   - Why normalization into canonical internal names is needed for analytics and integration.

3. **Association/authentication concepts (AARQ/AARE, LLS/HLS, security suites)**
   - Request/response association handshake.
   - Tradeoffs among authentication modes and security levels.

4. **Discovery and network scanning patterns**
   - IP range expansion, port probing, retry/timeout/concurrency design.
   - Distinguishing “reachable endpoint” from “identified meter.”

5. **Fingerprinting and vendor classification**
   - Constructing meter signatures from protocol/device features.
   - Mapping signatures to vendor/model confidence outcomes.

6. **Data modeling with Pydantic**
   - Strict API contracts (`MeterInstance`, `DiscoveryResult`, `Fingerprint`, etc.).
   - Benefits of typed schemas in protocol-heavy integrations.

7. **Service orchestration in FastAPI**
   - Route-to-service layering and dependency management.
   - API key middleware pattern and startup seeding behavior.

8. **Polyglot persistence strategy**
   - When to place data in SQL vs document stores.
   - Resilience pattern of DB-first with in-memory fallback.

9. **Frontend-backend contract discipline**
   - Aligning response shapes (`list` vs wrapped `items`).
   - Handling auth headers and env-driven endpoint configuration.

10. **Containerized platform operation**
   - Docker Compose services, local reproducibility, and environment-based toggles.

## Notes for maintainers / next improvements

- `discovery.py` currently defines `scan` twice; the second definition overrides the first. If intentional, this should be documented clearly. If not intentional, consolidating both implementations would remove ambiguity.
- Current frontend is dashboard-centric and can be extended into full operator workflows (instance creation, scan execution, profile export actions).
- Vendor classification is static-rule based today; a richer feature store or ML model could be plugged in later.

