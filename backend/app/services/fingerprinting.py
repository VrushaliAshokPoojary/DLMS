from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import settings
from app.models.core import Fingerprint, MeterInstance


class FingerprintingEngine:
    def build_fingerprint(self, meter: MeterInstance) -> Fingerprint:
        signature = f"{meter.vendor}:{meter.model}:{meter.authentication}:{meter.security_suite}"
        features = {
            "referencing": "LN" if meter.model.endswith("0") else "SN",
            "obis_count": str(len(meter.obis_objects)),
        }
        return Fingerprint(
            meter_id=meter.meter_id,
            vendor_signature=signature,
            features=features,
            created_at=datetime.utcnow(),
        )


class FingerprintLog:
    def __init__(self) -> None:
        self._logs: dict[str, Fingerprint] = {}
        self._collection = None
        self._init_db()

    def _init_db(self) -> None:
        try:
            client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=1000)
            client.admin.command("ping")
            self._collection = client[settings.mongo_db]["fingerprints"]
        except PyMongoError:
            self._collection = None

    def store(self, fingerprint: Fingerprint) -> None:
        self._logs[str(uuid4())] = fingerprint
        if not self._collection:
            return
        try:
            self._collection.insert_one(fingerprint.model_dump())
        except PyMongoError:
            return

    def list(self) -> list[Fingerprint]:
        if not self._collection:
            return list(self._logs.values())
        try:
            docs = list(self._collection.find({}, {"_id": 0}))
            return [Fingerprint(**doc) for doc in docs]
        except PyMongoError:
            return list(self._logs.values())
