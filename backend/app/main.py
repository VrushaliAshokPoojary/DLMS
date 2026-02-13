
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.core import (
    AssociationReport,
    DiscoveryRequest,
    MeterInstance,
    MeterTemplate,
    ObisNormalizationResult,
    VendorClassification,
)
from app.services.association import AssociationNegotiator
from app.services.discovery import DiscoveryEngine
from app.services.dlms_client import DlmsClient
from app.services.emulator import EmulatorRegistry, seed_registry
from app.services.fingerprinting import FingerprintLog, FingerprintingEngine
from app.services.obis import ObisNormalizer
from app.services.profiles import ProfileGenerator, ProfileRepository
from app.services.vendor import VendorClassifier

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

association_negotiator = AssociationNegotiator()
obis_normalizer = ObisNormalizer()
vendor_classifier = VendorClassifier()
dlms_client = DlmsClient()


@app.on_event("startup")
def seed_sample_data() -> None:
    if not settings.seed_sample_data:
        return
    if registry.list_instances():
        return
    for index, template in enumerate(registry.list_templates()):
        instance = registry.create_instance(
            vendor=template.vendor,
            model=template.model,
            ip_address="127.0.0.1",
            port=4059 + index,
        )
        fingerprint = fingerprinting_engine.build_fingerprint(instance)
        fingerprint_log.store(fingerprint)
        profile = profile_generator.build_profile(instance)
        profile_repo.store(profile)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid_api_key")


@app.get("/health", dependencies=[Depends(require_api_key)])

def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/emulators/templates", response_model=list[MeterTemplate], dependencies=[Depends(require_api_key)])

def list_templates() -> list[MeterTemplate]:
    return registry.list_templates()



@app.post("/emulators/instances", response_model=MeterInstance, dependencies=[Depends(require_api_key)])

def create_instance(vendor: str, model: str, ip_address: str, port: int = 4059) -> MeterInstance:
    return registry.create_instance(vendor, model, ip_address, port)



@app.get("/emulators/instances", response_model=list[MeterInstance], dependencies=[Depends(require_api_key)])

def list_instances() -> list[MeterInstance]:
    return registry.list_instances()



@app.post("/discovery/scan", dependencies=[Depends(require_api_key)])

def scan(request: DiscoveryRequest) -> dict[str, object]:
    results = discovery_engine.scan(request)
    return {"count": len(results), "results": results}



@app.get("/discovery/logs", dependencies=[Depends(require_api_key)])
def list_discovery_logs() -> dict[str, object]:
    return {"items": discovery_engine.list_logs()}


@app.post("/fingerprints/{meter_id}", dependencies=[Depends(require_api_key)])

def fingerprint_meter(meter_id: str) -> dict[str, object]:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        return {"error": "meter_not_found"}
    fingerprint = fingerprinting_engine.build_fingerprint(meter)
    fingerprint_log.store(fingerprint)
    return {"fingerprint": fingerprint}



@app.get("/fingerprints", dependencies=[Depends(require_api_key)])

def list_fingerprints() -> dict[str, object]:
    return {"items": fingerprint_log.list()}



@app.post("/profiles/{meter_id}", dependencies=[Depends(require_api_key)])

def build_profile(meter_id: str) -> dict[str, object]:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        return {"error": "meter_not_found"}
    profile = profile_generator.build_profile(meter)
    profile_repo.store(profile)
    return {"profile": profile}


@app.get("/profiles", dependencies=[Depends(require_api_key)])
def list_profiles() -> dict[str, object]:
    return {"items": profile_repo.list()}


@app.post("/associations/{meter_id}", response_model=AssociationReport, dependencies=[Depends(require_api_key)])
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
    if settings.dlms_adapter_url:
        return dlms_client.associate(meter)
    return association_negotiator.negotiate(meter)


@app.get("/obis/normalize/{meter_id}", response_model=ObisNormalizationResult, dependencies=[Depends(require_api_key)])
def normalize_obis(meter_id: str) -> ObisNormalizationResult:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        raise HTTPException(status_code=404, detail="meter_not_found")
    if settings.dlms_adapter_url:
        return dlms_client.fetch_obis(meter)
    return obis_normalizer.normalize(meter)


@app.get("/dlms/adapter/health", dependencies=[Depends(require_api_key)])
def adapter_health() -> dict[str, object]:
    return dlms_client.health()


@app.get("/vendors/classify/{meter_id}", response_model=VendorClassification, dependencies=[Depends(require_api_key)])
def classify_vendor(meter_id: str) -> VendorClassification:
    meter = next((m for m in registry.list_instances() if m.meter_id == meter_id), None)
    if not meter:
        raise HTTPException(status_code=404, detail="meter_not_found")
    return vendor_classifier.classify(meter)
