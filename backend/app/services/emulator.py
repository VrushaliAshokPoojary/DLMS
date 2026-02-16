from __future__ import annotations

from ipaddress import IPv4Address
from uuid import uuid4

from fastapi import HTTPException

from app.models.core import BulkInstanceCreateRequest, MeterInstance, MeterTemplate, ObisObject


class EmulatorRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, MeterTemplate] = {}
        self._instances: dict[str, MeterInstance] = {}

    @staticmethod
    def _template_key(vendor: str, model: str) -> str:
        return f"{vendor}:{model}"

    def register_template(self, template: MeterTemplate) -> None:
        key = self._template_key(template.vendor, template.model)
        self._templates[key] = template

    def create_template(self, template: MeterTemplate) -> MeterTemplate:
        key = self._template_key(template.vendor, template.model)
        if key in self._templates:
            raise HTTPException(status_code=409, detail="template_already_exists")
        self._templates[key] = template
        return template

    def list_templates(self) -> list[MeterTemplate]:
        return list(self._templates.values())


    @staticmethod
    def _default_template(vendor: str, model: str) -> MeterTemplate:
        return MeterTemplate(
            vendor=vendor,
            model=model,
            referencing="LN",
            authentication_modes=["None"],
            security_suites=[0],
            obis_objects=[
                ObisObject(
                    code="1-0:1.8.0",
                    description="Active energy import",
                    data_type="double",
                    unit="kWh",
                )
            ],
        )

    def create_instance(self, vendor: str, model: str, ip_address: str, port: int) -> MeterInstance:
        key = self._template_key(vendor, model)
        template = self._templates.get(key)
        if template is None:
            template = self._default_template(vendor, model)
            self._templates[key] = template

        meter_id = str(uuid4())
        instance = MeterInstance(
            meter_id=meter_id,
            vendor=template.vendor,
            model=template.model,
            ip_address=ip_address,
            port=port,
            authentication=template.authentication_modes[0],
            security_suite=template.security_suites[0],
            obis_objects=template.obis_objects,
        )
        self._instances[meter_id] = instance
        return instance

    def create_instances_bulk(self, request: BulkInstanceCreateRequest) -> list[MeterInstance]:
        base_ip = IPv4Address(request.base_ip)
        instances: list[MeterInstance] = []
        for idx in range(request.count):
            ip_address = str(base_ip + idx)
            port = request.start_port + idx
            instances.append(
                self.create_instance(
                    vendor=request.vendor,
                    model=request.model,
                    ip_address=ip_address,
                    port=port,
                )
            )
        return instances

    def list_instances(self) -> list[MeterInstance]:
        return list(self._instances.values())

    def find_instance(self, ip_address: str, port: int) -> MeterInstance | None:
        for instance in self._instances.values():
            if instance.ip_address == ip_address and instance.port == port:
                return instance
        return None


DEFAULT_TEMPLATES = [
    MeterTemplate(
        vendor="Acme Energy",
        model="A1000",
        referencing="LN",
        authentication_modes=["LLS", "HLS"],
        security_suites=[1, 2],
        obis_objects=[
            ObisObject(code="1-0:1.8.0", description="Active energy import", data_type="double", unit="kWh"),
            ObisObject(code="1-0:2.8.0", description="Active energy export", data_type="double", unit="kWh"),
        ],
    ),
    MeterTemplate(
        vendor="Zenith Power",
        model="Z900",
        referencing="SN",
        authentication_modes=["None", "LLS"],
        security_suites=[0, 1],
        obis_objects=[
            ObisObject(code="1-0:32.7.0", description="Voltage L1", data_type="double", unit="V"),
            ObisObject(code="1-0:52.7.0", description="Voltage L2", data_type="double", unit="V"),
        ],
    ),
]


def seed_registry(registry: EmulatorRegistry) -> None:
    for template in DEFAULT_TEMPLATES:
        registry.register_template(template)
