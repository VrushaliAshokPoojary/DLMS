from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.models.core import Fingerprint, MeterInstance


class FingerprintingEngine:
    def build_fingerprint(self, meter: MeterInstance) -> Fingerprint:
        signature = f"{meter.vendor}:{meter.model}:{meter.authentication}:{meter.security_suite}"
        features = {
            "referencing": "LN" if meter.model.endswith("0") else "SN",
            "obis_count": str(len(meter.obis_objects)),
        }
        return Fingerprint(
            meter_id=meter.meter_id,
            vendor_signature=signature,
            features=features,
            created_at=datetime.utcnow(),
        )


class FingerprintLog:
    def __init__(self) -> None:
        self._logs: dict[str, Fingerprint] = {}

    def store(self, fingerprint: Fingerprint) -> None:
        self._logs[str(uuid4())] = fingerprint

    def list(self) -> list[Fingerprint]:
        return list(self._logs.values())
