from __future__ import annotations

from datetime import datetime

from app.models.core import AssociationObjectList, AssociationReport, MeterInstance


class AssociationNegotiator:
    def negotiate(self, meter: MeterInstance) -> AssociationReport:
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

    def association_objects(self, meter: MeterInstance) -> AssociationObjectList:
        return AssociationObjectList(
            meter_id=meter.meter_id,
            objects=[obj.code for obj in meter.obis_objects],
            created_at=datetime.utcnow(),
        )
