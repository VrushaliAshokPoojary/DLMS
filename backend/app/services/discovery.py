from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.models.core import DiscoveryRequest, DiscoveryResult, MeterInstance
from app.services.emulator import EmulatorRegistry


class DiscoveryEngine:
    def __init__(self, registry: EmulatorRegistry) -> None:
        self._registry = registry

    def scan(self, request: DiscoveryRequest) -> list[DiscoveryResult]:
        results: list[DiscoveryResult] = []
        for instance in self._registry.list_instances():
            result = self._to_result(instance)
            results.append(result)
        if not results:
            results.append(
                DiscoveryResult(
                    meter_id=str(uuid4()),
                    ip_address="0.0.0.0",
                    port=request.ports[0],
                    discovered_at=datetime.utcnow(),
                    vendor=None,
                    model=None,
                    authentication=None,
                    security_suite=None,
                )
            )
        return results

    @staticmethod
    def _to_result(instance: MeterInstance) -> DiscoveryResult:
        return DiscoveryResult(
            meter_id=instance.meter_id,
            ip_address=instance.ip_address,
            port=instance.port,
            discovered_at=datetime.utcnow(),
            vendor=instance.vendor,
            model=instance.model,
            authentication=instance.authentication,
            security_suite=instance.security_suite,
        )
