from __future__ import annotations

from datetime import datetime

from app.models.core import MeterInstance, ObisNormalizationResult

DEFAULT_NORMALIZATION = {
    "1-0:1.8.0": "energy_active_import_kwh",
    "1-0:2.8.0": "energy_active_export_kwh",
    "1-0:32.7.0": "voltage_l1_v",
    "1-0:52.7.0": "voltage_l2_v",
}


class ObisNormalizer:
    def normalize(self, meter: MeterInstance) -> ObisNormalizationResult:
        normalized = {
            obj.code: DEFAULT_NORMALIZATION.get(obj.code, obj.code.replace(".", "_").replace(":", "_"))
            for obj in meter.obis_objects
        }
        return ObisNormalizationResult(
            meter_id=meter.meter_id,
            normalized=normalized,
            created_at=datetime.utcnow(),
        )
