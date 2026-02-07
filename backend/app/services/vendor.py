from __future__ import annotations

from datetime import datetime

from app.models.core import MeterInstance, VendorClassification

VENDOR_SIGNATURES = {
    "Acme Energy": ("Acme", 0.92),
    "Zenith Power": ("Zenith", 0.9),
}


class VendorClassifier:
    def classify(self, meter: MeterInstance) -> VendorClassification:
        classification, confidence = VENDOR_SIGNATURES.get(
            meter.vendor,
            ("Unknown", 0.5),
        )
        return VendorClassification(
            meter_id=meter.meter_id,
            vendor=meter.vendor,
            model=meter.model,
            classification=classification,
            confidence=confidence,
            created_at=datetime.utcnow(),
        )
