# Software-Defined Universal DLMS Auto-Discovery & Fingerprinting Platform
## Repository Analysis & Technical Defense Guide (SRS-aligned)

This guide analyzes the current repository implementation against your provided SRS and gives a presentation-ready technical reference.

---

## 1) Achievements vs Not Achieved Tasks (FR-1 to FR-15)

> Interpretation rule used: status is based on **current repository behavior**. If behavior is simulated and end-to-end callable via API, it is marked **ACHIEVED (Prototype)**. If a production-grade requirement is absent (for example true cryptographic DLMS stack), it is marked **NOT ACHIEVED (Production Depth)**.

| FR | Requirement | Status | How/Why (Repository Evidence) |
|---|---|---|---|
| FR-1 | Emulate DLMS meters with configurable vendor templates | **ACHIEVED (Prototype)** | `EmulatorRegistry` supports template registry + runtime template creation + instance creation. Default templates are seeded and API endpoints expose template and instance lifecycle. |
| FR-2 | Simulate LN and SN referencing meters | **ACHIEVED (Prototype)** | Templates include `referencing: "LN"` and `"SN"`; model enforces `Literal["LN","SN"]`. |
| FR-3 | Expose configurable OBIS object lists | **ACHIEVED (Prototype)** | Template schema includes `obis_objects`; runtime template API accepts OBIS list and instances carry OBIS list. |
| FR-4 | Scan IP ranges for DLMS endpoints | **ACHIEVED (Prototype)** | Discovery expands CIDR targets and probes each host/port via thread pool. |
| FR-5 | Detect DLMS communication ports | **ACHIEVED (Prototype)** | Discovery uses socket connect to determine reachable ports and returns discovered endpoints. |
| FR-6 | Perform association handshake (AARQ/AARE) | **ACHIEVED (Simulated) / NOT ACHIEVED (Native protocol)** | Local negotiator builds synthetic AARQ/AARE strings; true protocol can only come via external adapter (`DLMS_ADAPTER_URL`). |
| FR-7 | Detect auth modes (None, LLS, HLS) | **ACHIEVED (Template-derived) / NOT ACHIEVED (Protocol-negotiated)** | Auth mode is selected from template during instance creation and returned by association/classification flows; no native wire-level negotiation engine exists. |
| FR-8 | Identify security suites (0/1/2) | **ACHIEVED (Template-derived) / NOT ACHIEVED (Protocol-negotiated)** | Security suite is template-derived and surfaced via APIs; native cryptographic negotiation is not implemented in backend core. |
| FR-9 | Extract association object lists | **ACHIEVED (Prototype)** | Object list endpoint returns meter OBIS codes from simulator, or adapter output when configured. |
| FR-10 | Normalize OBIS mappings | **ACHIEVED (Prototype)** | OBIS normalizer endpoint exists and returns normalized map from local rules or adapter data path. |
| FR-11 | Generate vendor protocol fingerprints | **ACHIEVED (Prototype)** | Fingerprint engine builds `vendor_signature` + features and stores in Mongo (or memory fallback). |
| FR-12 | Classify meter manufacturer | **ACHIEVED (Prototype)** | Static signature-based classifier maps vendors to labels/confidence. |
| FR-13 | Generate meter configuration profiles | **ACHIEVED (Prototype)** | Profile generator builds profile + stores in PostgreSQL `meter_profiles`; export endpoint wraps profile with schema version metadata. |
| FR-14 | Expose REST APIs for integration | **ACHIEVED** | FastAPI exposes health/summary/emulator/discovery/fingerprint/profile/association/OBIS/vendor endpoints. |
| FR-15 | Support bulk discovery operations | **ACHIEVED (Prototype)** | CIDR range scanning + concurrency + retries in discovery engine; bulk instance provisioning also exists (`/emulators/instances/bulk`). |

### Practical reason for gaps
Requirements FR-6/7/8 in strict utility-grade form require a full DLMS protocol stack (secure associations, key management, APDU parsing, ciphered traffic handling). This repository deliberately keeps backend core lightweight and supports real stack integration through `DLMS_ADAPTER_URL` instead.

---

## 2) Complete End-to-End Working Explanation

### A. Virtual meter creation lifecycle
1. On startup, default templates are seeded (`Acme Energy A1000`, `Zenith Power Z900`).
2. User lists templates or creates new templates through API.
3. User creates single or bulk instances.
4. Instance inherits template auth mode/security suite/OBIS objects and receives generated `meter_id`.

### B. Discovery lifecycle
1. Client sends `DiscoveryRequest` with `ip_range`, `ports`, `timeout_seconds`, `retries`, `max_concurrency`.
2. Engine expands CIDR into host:port targets.
3. Thread pool probes each target using socket connection.
4. For reachable target:
   - If matched to known emulator instance → enriched result (vendor/model/auth/suite).
   - Else → generic reachable endpoint record.
5. Discovery scan metadata is logged (MongoDB or memory fallback).

### C. Association (AARQ/AARE) lifecycle
1. Client calls `POST /associations/{meter_id}`.
2. If `DLMS_ADAPTER_URL` configured → backend forwards to adapter `/associate`.
3. Else simulator returns synthetic AARQ/AARE report based on meter authentication/suite.

### D. Auth + security suite detection logic
- In current repository, auth/suite are **meter-template-derived attributes** attached at instance creation.
- They are surfaced in association reports and other outputs.
- With external adapter enabled, these can represent protocol-derived values from real DLMS communication.

### E. OBIS extraction + normalization lifecycle
1. `GET /associations/objects/{meter_id}` returns association object list from simulator (OBIS codes) or adapter.
2. `GET /obis/normalize/{meter_id}` returns normalized OBIS dictionary from local module or adapter.

### F. Fingerprinting + vendor classification lifecycle
1. Fingerprinting engine creates vendor signature: `vendor:model:auth:suite`.
2. Feature map is generated (`referencing`, `obis_count`).
3. Vendor classifier applies signature rules and confidence scoring.
4. Fingerprint record stored in MongoDB `fingerprints` (fallback memory).

### G. Meter profile generation + integration API lifecycle
1. `POST /profiles/{meter_id}` builds profile (`profile_id`, meter identity, `obis_map`).
2. Repository stores profile in PostgreSQL table `meter_profiles`.
3. `GET /profiles/{meter_id}/export` exposes schema-versioned export contract for HES/MDMS integration.

---

## 3) Data Flow & Storage Architecture

## Data generated by stage
- **Emulator stage**: templates, instances, auth mode, suite, OBIS catalog.
- **Discovery stage**: scan request metadata, discovered endpoints, reachability.
- **Association stage**: association status, AARQ/AARE payload summary.
- **Fingerprinting stage**: vendor signature, feature map, classification label.
- **Profile stage**: normalized profile payload for integration.

## Storage mapping
- **PostgreSQL**
  - Table: `meter_profiles`
  - Stores profile records (`profile_id`, `meter_id`, vendor/model, `obis_map`, timestamp).
- **MongoDB**
  - Collection: `fingerprints`
  - Collection: `discovery_logs`
- **Memory fallback**
  - Used automatically if DB unavailable (both discovery and fingerprint/profile paths include fallback behavior).

## How logs/OBIS/signatures are organized
- Discovery logs are structured as `DiscoveryLog` model (scan id, range, ports, target/discovered counts, timing).
- OBIS mappings are represented as dictionary maps in profile and normalization responses.
- Vendor signatures are simple concatenated identifiers plus low-dimensional feature map.

## Verification commands
```bash
# API checks
curl http://localhost:8000/health
curl http://localhost:8000/summary
curl http://localhost:8000/discovery/logs
curl http://localhost:8000/fingerprints
curl http://localhost:8000/profiles

# PostgreSQL proof
docker compose exec postgres psql -U dlms -d dlms -c "SELECT profile_id,meter_id,vendor,model,created_at FROM meter_profiles ORDER BY created_at DESC LIMIT 10;"

# MongoDB proof
docker compose exec mongo mongosh --eval "use dlms; db.fingerprints.find({}, {_id:0}).limit(5).pretty(); db.discovery_logs.find({}, {_id:0}).limit(5).pretty();"
```

---

## 4) System Execution Guidelines (Step-by-step)

## A. Environment setup
```bash
cp .env.example .env
```
Recommended demo values:
- `API_KEY=`
- `SEED_SAMPLE_DATA=true`
- `VITE_API_URL=http://localhost:8000`

## B. Docker run (recommended)
```bash
make up
# or
docker compose up --build
```
Endpoints:
- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`
- Nginx: `http://localhost:8080`

Lifecycle:
```bash
make ps
make logs
make down
```

## C. Local run (without Docker)
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Use local DB hosts when outside Compose:
- `POSTGRES_HOST=localhost`
- `MONGO_URL=mongodb://localhost:27017`

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## D. Validate emulator + discovery + profiling
```bash
# 1) Create meter
curl -X POST "http://localhost:8000/emulators/instances?vendor=Acme%20Energy&model=A1000&ip_address=127.0.0.1&port=4059"

# 2) Discovery
curl -X POST "http://localhost:8000/discovery/scan" -H "Content-Type: application/json" -d '{"ip_range":"127.0.0.0/30","ports":[4059],"timeout_seconds":0.5,"max_concurrency":20,"retries":1}'

# 3) Full protocol workflow
curl -X POST "http://localhost:8000/fingerprints/<METER_ID>"
curl -X POST "http://localhost:8000/profiles/<METER_ID>"
curl -X POST "http://localhost:8000/associations/<METER_ID>"
curl "http://localhost:8000/associations/objects/<METER_ID>"
curl "http://localhost:8000/obis/normalize/<METER_ID>"
curl "http://localhost:8000/vendors/classify/<METER_ID>"
```

## E. Gurux/OpenMUC + Wireshark note
- Repository currently integrates real stack via **adapter URL** (`DLMS_ADAPTER_URL`).
- Gurux/OpenMUC execution commands are adapter-specific and are **not implemented in this repository tree**.
- Practical approach: run adapter as a separate service and point backend to it; then use Wireshark on adapter traffic path for packet-level validation.

---

## 5) Presentation Script (Technical Defense Ready)

## Slide 1 — Problem
Utility onboarding of heterogeneous DLMS meters is slow and hardware-dependent. Physical-lab-only validation limits scale and repeatability.

## Slide 2 — Solution
We built a software-defined DLMS interoperability lab that simulates meters, auto-discovers endpoints, fingerprints protocol behavior, normalizes OBIS data, and exports meter profiles through REST APIs.

## Slide 3 — Architecture
React dashboard drives FastAPI orchestrator. Backend integrates PostgreSQL for durable profiles and MongoDB for discovery/fingerprint telemetry. Optional external DLMS adapter provides real protocol-depth operations.

## Slide 4 — Core modules
1. Emulator engine
2. Discovery engine
3. Association/auth negotiator
4. OBIS normalization
5. Fingerprinting + classification
6. Profile generator + export API

## Slide 5 — Demo flow
Create virtual meter → scan network range → run association + object list + OBIS normalization → generate fingerprint/classification → persist profile → verify data in SQL/Mongo.

## Slide 6 — Results
- Full API-driven prototype is operational.
- Polyglot persistence and graceful fallback improve resilience.
- Bulk simulation + concurrent discovery support scale-oriented testing.

## Slide 7 — Limitations
- Native DLMS cryptographic handshake parsing is adapter-dependent.
- Vendor classification is static-rule based.
- Repository lacks benchmark artifacts proving 10k-meter acceptance criteria.

## Slide 8 — Next phase
Integrate production-grade adapter, build labeled vendor dataset, implement RBAC/TLS hardening, and produce formal performance reports.

---

## 6) Interview Questions & Suggested Answers

1. **Q: Is this a real DLMS stack or simulation?**  
   **A:** Core backend is simulation-first for reproducibility; real protocol depth is enabled through an external adapter using `DLMS_ADAPTER_URL`.

2. **Q: Why both PostgreSQL and MongoDB?**  
   **A:** Profiles are structured and relational (`meter_profiles`), while discovery/fingerprint logs are document-style telemetry better suited to MongoDB.

3. **Q: How is discovery scaled?**  
   **A:** Discovery expands CIDR ranges and probes with `ThreadPoolExecutor` using configurable concurrency, timeout, and retry controls.

4. **Q: How do you detect auth mode/security suite?**  
   **A:** In prototype mode they are template-derived. In integration mode adapter responses can provide negotiated values.

5. **Q: How are OBIS objects normalized?**  
   **A:** Normalization endpoint returns canonical mappings from local normalization logic (or adapter response).

6. **Q: What makes fingerprinting explainable?**  
   **A:** Signature + explicit feature map (`referencing`, `obis_count`) are returned and stored, making decisions auditable.

7. **Q: How does the system behave when databases fail?**  
   **A:** It degrades to in-memory storage for key paths, allowing demo continuity while persistence is unavailable.

8. **Q: How is integration to HES/MDMS achieved?**  
   **A:** REST APIs expose profiles and export payload (`/profiles/{meter_id}/export`) with schema metadata.

---

## 7) Reasons for Success & Limitations

## Why modules perform well (prototype scope)
- **Strong API contracting** via Pydantic models.
- **Modular service boundaries** (emulator/discovery/profile/fingerprint/association separated).
- **Resilience pattern** (DB-first + memory fallback).
- **Operational simplicity** through Docker Compose and predictable endpoints.

## Limitations
- No embedded native Gurux/OpenMUC protocol engine in backend core.
- Static-rule vendor classifier (no ML training pipeline or benchmark dataset).
- SRS NFR targets (10k performance, 85%+ classification, TLS/RBAC) are not evidenced by committed benchmark/security artifacts.

---

## 8) NFR Reality Check (Repository Evidence)

| NFR Area | SRS Expectation | Current State |
|---|---|---|
| Performance | ≤60 sec discovery/meter, 10k virtual meters | Concurrency controls and bulk provisioning exist, but no committed benchmark report proving target. |
| Security | TLS1.2+, RBAC | Optional API key auth exists; TLS termination/RBAC framework not implemented in app layer. |
| Scalability | Containerized + horizontal scaling | Dockerized services present; no Kubernetes manifests/autoscaling configs in repo. |
| Reliability | Retry + fault tolerance | Discovery retries and in-memory fallback implemented; no chaos/failover test artifacts. |

---

## 9) Recommended 7-day action plan (P0/P1/P2)

### P0 (must-have)
- Connect and validate real adapter (`DLMS_ADAPTER_URL`).
- Add reproducible benchmark scripts + result artifacts (latency/throughput).
- Add security baseline (TLS reverse proxy hardening + role model design).

### P1 (high-value)
- Enrich vendor classifier features and collect labeled evaluation dataset.
- Add dashboard pages for discovery logs and exported profiles.
- Add API integration examples for HES/MDMS payload consumption.

### P2 (next-level)
- Kubernetes deployment manifests and HPA strategy.
- Observability stack (metrics + traces + alert rules).
- Formal test matrix for multi-vendor protocol deviations.

---

## 10) Final technical conclusion

This repository is a strong **software-defined DLMS prototype platform** with complete workflow APIs and practical persistence architecture. It is highly suitable for demonstrations, interoperability research, and integration prototyping. To fully satisfy utility-grade SRS expectations, the next engineering phase should focus on native/proxy protocol-depth validation, measurable performance proof, and enterprise security/operability hardening.
