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


class DiscoveryRequest(BaseModel):
    ip_range: str
    ports: list[int] = Field(default_factory=lambda: [4059])
    max_concurrency: int = 200


class DiscoveryResult(BaseModel):
    meter_id: str
    ip_address: str
    port: int
    discovered_at: datetime
    vendor: str | None = None
    model: str | None = None
    authentication: str | None = None
    security_suite: int | None = None


class Fingerprint(BaseModel):
    meter_id: str
    vendor_signature: str
    features: dict[str, str]
    created_at: datetime


class MeterProfile(BaseModel):
    profile_id: str
    meter_id: str
    vendor: str
    model: str
    obis_map: dict[str, str]
    created_at: datetime


class AssociationReport(BaseModel):
    meter_id: str
    status: Literal["success", "failed"]
    authentication: str
    security_suite: int
    aarq: str
    aare: str
    created_at: datetime
