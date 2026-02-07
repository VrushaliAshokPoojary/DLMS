from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime

from app.models.core import AssociationReport, DiscoveryRequest, MeterInstance, MeterTemplate
from app.services.discovery import DiscoveryEngine
from app.services.emulator import EmulatorRegistry, seed_registry
from app.services.fingerprinting import FingerprintLog, FingerprintingEngine
from app.services.profiles import ProfileGenerator, ProfileRepository

app = FastAPI(title="DLMS Auto-Discovery Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

registry = EmulatorRegistry()
seed_registry(registry)

discovery_engine = DiscoveryEngine(registry)
fingerprinting_engine = FingerprintingEngine()
fingerprint_log = FingerprintLog()
profile_generator = ProfileGenerator()
profile_repo = ProfileRepository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/emulators/templates", response_model=list[MeterTemplate])
def list_templates() -> list[MeterTemplate]:
    return registry.list_templates()


@app.post("/emulators/instances", response_model=MeterInstance)
def create_instance(vendor: str, model: str, ip_address: str, port: int = 4059) -> MeterInstance:
    return registry.create_instance(vendor, model, ip_address, port)


@app.get("/emulators/instances", response_model=list[MeterInstance])
def list_instances() -> list[MeterInstance]:
    return registry.list_instances()


@app.post("/discovery/scan")
def scan(request: DiscoveryRequest) -> dict[str, object]:
    results = discovery_engine.scan(request)
    return {"count": len(results), "results": results}


@app.post("/fingerprints/{meter_id}")
def fingerprint_meter(meter_id: str) -> dict[str, object]:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        return {"error": "meter_not_found"}
    fingerprint = fingerprinting_engine.build_fingerprint(meter)
    fingerprint_log.store(fingerprint)
    return {"fingerprint": fingerprint}


@app.get("/fingerprints")
def list_fingerprints() -> dict[str, object]:
    return {"items": fingerprint_log.list()}


@app.post("/profiles/{meter_id}")
def build_profile(meter_id: str) -> dict[str, object]:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        return {"error": "meter_not_found"}
    profile = profile_generator.build_profile(meter)
    profile_repo.store(profile)
    return {"profile": profile}


@app.get("/profiles")
def list_profiles() -> dict[str, object]:
    return {"items": profile_repo.list()}


@app.post("/associations/{meter_id}", response_model=AssociationReport)
def associate_meter(meter_id: str) -> AssociationReport:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        return AssociationReport(
            meter_id=meter_id,
            status="failed",
            authentication="None",
            security_suite=0,
            aarq="",
            aare="",
            created_at=datetime.utcnow(),
        )
    aarq = f"AARQ(auth={meter.authentication},suite={meter.security_suite})"
    aare = f"AARE(result=accepted,vendor={meter.vendor},model={meter.model})"
    return AssociationReport(
        meter_id=meter_id,
        status="success",
        authentication=meter.authentication,
        security_suite=meter.security_suite,
        aarq=aarq,
        aare=aare,
        created_at=datetime.utcnow(),
    )
