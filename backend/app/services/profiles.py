from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.models.core import MeterInstance, MeterProfile, ProfileExport


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

    @staticmethod
    def export_profile(profile: MeterProfile) -> ProfileExport:
        return ProfileExport(
            schema_version="1.0",
            exported_at=datetime.utcnow(),
            profile=profile,
        )


class ProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, MeterProfile] = {}
        self._engine = None
        self._table = None
        self._init_db()

    def _init_db(self) -> None:
        try:
            self._engine = create_engine(settings.postgres_dsn, future=True)
            metadata = MetaData()
            self._table = Table(
                "meter_profiles",
                metadata,
                Column("profile_id", String, primary_key=True),
                Column("meter_id", String, nullable=False),
                Column("vendor", String, nullable=False),
                Column("model", String, nullable=False),
                Column("obis_map", JSON, nullable=False),
                Column("created_at", DateTime, nullable=False),
            )
            metadata.create_all(self._engine)
        except SQLAlchemyError:
            self._engine = None
            self._table = None

    def store(self, profile: MeterProfile) -> None:
        self._profiles[profile.profile_id] = profile

        if self._engine is None or self._table is None:
            return

        try:
            with self._engine.begin() as conn:
                conn.execute(
                    self._table.insert().values(
                        profile_id=profile.profile_id,
                        meter_id=profile.meter_id,
                        vendor=profile.vendor,
                        model=profile.model,
                        obis_map=profile.obis_map,
                        created_at=profile.created_at,
                    )
                )
        except SQLAlchemyError:
            return

    def list(self) -> list[MeterProfile]:
        if self._engine is None or self._table is None:
            return list(self._profiles.values())

        try:
            with self._engine.begin() as conn:
                rows = conn.execute(select(self._table)).mappings().all()

            return [
                MeterProfile(
                    profile_id=row["profile_id"],
                    meter_id=row["meter_id"],
                    vendor=row["vendor"],
                    model=row["model"],
                    obis_map=row["obis_map"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]
        except SQLAlchemyError:
            return list(self._profiles.values())

    def latest_by_meter_id(self, meter_id: str) -> MeterProfile | None:
        profiles = [profile for profile in self.list() if profile.meter_id == meter_id]
        if not profiles:
            return None
        return sorted(profiles, key=lambda item: item.created_at, reverse=True)[0]
