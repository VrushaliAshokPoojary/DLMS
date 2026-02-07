from __future__ import annotations

from collections import defaultdict
from uuid import uuid4

from app.models.core import MeterInstance, MeterTemplate, ObisObject


class EmulatorRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, MeterTemplate] = {}
        self._instances: dict[str, MeterInstance] = {}

    def register_template(self, template: MeterTemplate) -> None:
        key = f"{template.vendor}:{template.model}"
        self._templates[key] = template

    def list_templates(self) -> list[MeterTemplate]:
        return list(self._templates.values())

    def create_instance(self, vendor: str, model: str, ip_address: str, port: int) -> MeterInstance:
        key = f"{vendor}:{model}"
        template = self._templates[key]
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
