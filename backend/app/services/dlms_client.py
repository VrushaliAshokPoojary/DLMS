from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests

from app.config import settings
from app.models.core import AssociationReport, MeterInstance, ObisNormalizationResult


@dataclass
class DlmsClientResult:
    association: AssociationReport
    obis_objects: dict[str, str]


class DlmsClient:
    def __init__(self) -> None:
        self._adapter_url = settings.dlms_adapter_url

    def associate(self, meter: MeterInstance) -> AssociationReport:
        if self._adapter_url:
            payload = {
                "meter_id": meter.meter_id,
                "ip_address": meter.ip_address,
                "port": meter.port,
                "authentication": meter.authentication,
                "security_suite": meter.security_suite,
            }
            response = requests.post(f"{self._adapter_url}/associate", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return AssociationReport(
                meter_id=meter.meter_id,
                status=data.get("status", "failed"),
                authentication=data.get("authentication", meter.authentication),
                security_suite=data.get("security_suite", meter.security_suite),
                aarq=data.get("aarq", ""),
                aare=data.get("aare", ""),
                created_at=datetime.utcnow(),
            )
        aarq = f"AARQ(auth={meter.authentication},suite={meter.security_suite})"
        aare = f"AARE(result=accepted,vendor={meter.vendor},model={meter.model})"
        return AssociationReport(
            meter_id=meter.meter_id,
            status="success",
            authentication=meter.authentication,
            security_suite=meter.security_suite,
            aarq=aarq,
            aare=aare,
            created_at=datetime.utcnow(),
        )

    def fetch_obis(self, meter: MeterInstance) -> ObisNormalizationResult:
        if self._adapter_url:
            payload = {
                "meter_id": meter.meter_id,
                "ip_address": meter.ip_address,
                "port": meter.port,
            }
            response = requests.post(f"{self._adapter_url}/obis", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return ObisNormalizationResult(
                meter_id=meter.meter_id,
                normalized=data.get("normalized", {}),
                created_at=datetime.utcnow(),
            )
        normalized = {obj.code: obj.description for obj in meter.obis_objects}
        return ObisNormalizationResult(
            meter_id=meter.meter_id,
            normalized=normalized,
            created_at=datetime.utcnow(),
        )

    def health(self) -> dict[str, Any]:
        if not self._adapter_url:
            return {"status": "disabled"}
        response = requests.get(f"{self._adapter_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()
