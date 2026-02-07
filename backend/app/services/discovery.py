from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from ipaddress import ip_network
import socket
from uuid import uuid4

from app.models.core import DiscoveryRequest, DiscoveryResult, MeterInstance
from app.services.emulator import EmulatorRegistry


class DiscoveryEngine:
    def __init__(self, registry: EmulatorRegistry) -> None:
        self._registry = registry

    def scan(self, request: DiscoveryRequest) -> list[DiscoveryResult]:
        targets = self._expand_targets(request.ip_range, request.ports)
        results: list[DiscoveryResult] = []
        if not targets:
            return results

        with ThreadPoolExecutor(max_workers=request.max_concurrency) as executor:
            futures = [executor.submit(self._probe_target, ip, port) for ip, port in targets]
            for future in as_completed(futures):
                target_result = future.result()
                if target_result:
                    results.append(target_result)
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

    @staticmethod
    def _expand_targets(ip_range: str, ports: list[int]) -> list[tuple[str, int]]:
        network = ip_network(ip_range, strict=False)
        targets: list[tuple[str, int]] = []
        for host in network.hosts():
            for port in ports:
                targets.append((str(host), port))
        return targets

    def _probe_target(self, ip_address: str, port: int) -> DiscoveryResult | None:
        if not self._is_port_open(ip_address, port):
            return None
        instance = self._registry.find_instance(ip_address, port)
        if instance:
            return self._to_result(instance)
        return DiscoveryResult(
            meter_id=str(uuid4()),
            ip_address=ip_address,
            port=port,
            discovered_at=datetime.utcnow(),
            vendor=None,
            model=None,
            authentication=None,
            security_suite=None,
        )

    @staticmethod
    def _is_port_open(ip_address: str, port: int, timeout: float = 0.5) -> bool:
        try:
            with socket.create_connection((ip_address, port), timeout=timeout):
                return True
        except OSError:
            return False
