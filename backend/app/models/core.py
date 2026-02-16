from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ObisObject(BaseModel):
    code: str = Field(..., example="1-0:1.8.0")
    description: str
    data_type: str
    unit: str | None = None


class MeterTemplate(BaseModel):
    vendor: str
    model: str
    referencing: Literal["LN", "SN"]

    authentication_modes: list[Literal["None", "LLS", "HLS"]] = Field(default_factory=lambda: ["LLS"])
    security_suites: list[Literal[0, 1, 2]] = Field(default_factory=lambda: [1])

    obis_objects: list[ObisObject]


class MeterInstance(BaseModel):
    meter_id: str
    vendor: str
    model: str
    ip_address: str
    port: int
    authentication: Literal["None", "LLS", "HLS"]
    security_suite: Literal[0, 1, 2]
    obis_objects: list[ObisObject]


class BulkInstanceCreateRequest(BaseModel):
    vendor: str
    model: str
    base_ip: str
    start_port: int = 4059
    count: int = Field(default=10, ge=1, le=10000)


class BulkInstanceCreateResult(BaseModel):
    created: int
    instances: list[MeterInstance]


class DiscoveryRequest(BaseModel):
    ip_range: str
    ports: list[int] = Field(default_factory=lambda: [4059])
    max_concurrency: int = 200

    timeout_seconds: float = 0.5
    retries: int = 1


class DiscoveryResult(BaseModel):
    meter_id: str
    ip_address: str
    port: int
    discovered_at: datetime
    vendor: str | None = None
    model: str | None = None
    authentication: str | None = None
    security_suite: int | None = None

    reachable: bool = True


class DiscoveryLog(BaseModel):
    scan_id: str
    ip_range: str
    ports: list[int]
    total_targets: int
    discovered: int
    started_at: datetime
    completed_at: datetime


class Fingerprint(BaseModel):
    meter_id: str
    vendor_signature: str
    features: dict[str, str]
    created_at: datetime

    vendor_classification: str | None = None


class MeterProfile(BaseModel):
    profile_id: str
    meter_id: str
    vendor: str
    model: str
    obis_map: dict[str, str]
    created_at: datetime


class ProfileExport(BaseModel):
    schema_version: str
    exported_at: datetime
    profile: MeterProfile


class AssociationReport(BaseModel):
    meter_id: str
    status: Literal["success", "failed"]
    authentication: str
    security_suite: int
    aarq: str
    aare: str
    created_at: datetime


class AssociationObjectList(BaseModel):
    meter_id: str
    objects: list[str]
    created_at: datetime


class ObisNormalizationResult(BaseModel):
    meter_id: str
    normalized: dict[str, str]
    created_at: datetime


class VendorClassification(BaseModel):
    meter_id: str
    vendor: str
    model: str
    classification: str
    confidence: float
    created_at: datetime
