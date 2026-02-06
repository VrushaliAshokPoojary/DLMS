from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.models.core import MeterInstance, MeterProfile


class ProfileGenerator:
    def build_profile(self, meter: MeterInstance) -> MeterProfile:
        return MeterProfile(
            profile_id=str(uuid4()),
            meter_id=meter.meter_id,
            vendor=meter.vendor,
            model=meter.model,
            obis_map={obj.code: obj.description for obj in meter.obis_objects},
            created_at=datetime.utcnow(),
        )


class ProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, MeterProfile] = {}

    def store(self, profile: MeterProfile) -> None:
        self._profiles[profile.profile_id] = profile

    def list(self) -> list[MeterProfile]:
        return list(self._profiles.values())
