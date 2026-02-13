from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from ipaddress import ip_network
import socket
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import settings
from app.models.core import DiscoveryLog, DiscoveryRequest, DiscoveryResult, MeterInstance
from app.services.emulator import EmulatorRegistry


class DiscoveryEngine:
    def __init__(self, registry: EmulatorRegistry) -> None:
        self._registry = registry
        self._collection = None
        self._memory_logs: list[DiscoveryLog] = []
        self._init_db()

    def _init_db(self) -> None:
        try:
            client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=1000)
            client.admin.command("ping")
            self._collection = client[settings.mongo_db]["discovery_logs"]
        except PyMongoError:
            self._collection = None

    def scan(self, request: DiscoveryRequest) -> list[DiscoveryResult]:
        started_at = datetime.utcnow()
        targets = self._expand_targets(request.ip_range, request.ports)
        results: list[DiscoveryResult] = []

        if not targets:
            return results

        with ThreadPoolExecutor(max_workers=request.max_concurrency) as executor:
            futures = [
                executor.submit(
                    self._probe_target,
                    ip,
                    port,
                    request.timeout_seconds,
                    request.retries,
                )
                for ip, port in targets
            ]
            for future in as_completed(futures):
                target_result = future.result()
                if target_result:
                    results.append(target_result)

        self._store_log(request, len(targets), len(results), started_at)
        return results

    def list_logs(self) -> list[DiscoveryLog]:
        if not self._collection:
            return list(self._memory_logs)
        try:
            docs = list(self._collection.find({}, {"_id": 0}))
            return [DiscoveryLog(**doc) for doc in docs]
        except PyMongoError:
            return list(self._memory_logs)

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

    def _probe_target(
        self,
        ip_address: str,
        port: int,
        timeout_seconds: float,
        retries: int,
    ) -> DiscoveryResult | None:
        if not self._is_port_open(ip_address, port, timeout_seconds, retries):
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
            reachable=True,
        )

    @staticmethod
    def _is_port_open(
        ip_address: str,
        port: int,
        timeout: float = 0.5,
        retries: int = 1,
    ) -> bool:
        for _ in range(max(retries, 1)):
            try:
                with socket.create_connection((ip_address, port), timeout=timeout):
                    return True
            except OSError:
                continue
        return False

    def _store_log(
        self,
        request: DiscoveryRequest,
        total_targets: int,
        discovered: int,
        started_at: datetime,
    ) -> None:
        log = DiscoveryLog(
            scan_id=str(uuid4()),
            ip_range=request.ip_range,
            ports=request.ports,
            total_targets=total_targets,
            discovered=discovered,
            started_at=started_at,
            completed_at=datetime.utcnow(),
        )
        self._memory_logs.append(log)

        if not self._collection:
            return
        try:
            self._collection.insert_one(log.model_dump())
        except PyMongoError:
            return
