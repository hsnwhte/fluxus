from pydantic import ValidationError
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fluxus.exceptions import errors
from fluxus.enums import Phase, ContentFormat, RunStatus
from fluxus.models.orm import (
    PayloadRecord,
    PipelineRunRecord,
    RegistryEntry,
    FetchCache,
)
from fluxus.models.dto import RegistryRecord, FetchCacheData


class PipelineRunRecordsSQLite:
    def __init__(self, session: Session):
        self.session = session

    def register_run(self) -> int:
        run = PipelineRunRecord()
        self.session.add(run)
        self.session.commit()
        return run.run_id

    def update_record(
        self,
        *,
        run_id: int,
        status: RunStatus,
        phase: Phase | None = None,
        entry_id: int | None = None,
    ) -> int:
        record = self.session.get(PipelineRunRecord, run_id)
        record.status = status
        record.interrupted_phase = phase
        record.interrupted_after_entry_id = entry_id
        self.session.commit()
        return run_id


class FetchCacheStoreSQLite:
    def __init__(self, session: Session):
        self.session = session

    def save(self, *, api_url: str, registry_address: int, payload_address: str) -> str:
        cache = FetchCache(
            api_url=api_url,
            registry_address=registry_address,
            payload_address=payload_address,
        )
        self.session.add(cache)
        self.session.commit()
        return api_url

    def load(self, *, api_url: str) -> FetchCacheData:
        db_cache = self.session.get(FetchCache, api_url)
        if db_cache is None or not db_cache.is_active:
            raise errors.FetchCacheNotFoundError(
                "Fetch cache does not exist or was deleted"
            )
        cache = FetchCacheData(
            api_url=db_cache.api_url,
            registry_address=db_cache.registry_address,
            payload_address=db_cache.payload_address,
            created_at=db_cache.created_at,
            is_active=db_cache.is_active,
        )
        return cache


class RegistryStoreSQLite:
    def __init__(self, session: Session):
        self.session = session

    def save_entry(
        self,
        *,
        run_id: int,
        phase: Phase,
        content_format: ContentFormat,
        strategy_name: str,
        content_hash: str,
        address: str,
    ) -> int:
        entry = RegistryEntry(
            run_id=run_id,
            phase=phase,
            content_format=content_format,
            strategy_name=strategy_name,
            content_hash=content_hash,
            address=address,
        )
        self.session.add(entry)
        self.session.commit()
        return entry.id

    def get_entry_by_id(self, *, entry_id: int) -> RegistryRecord:
        """Retreives entry object by entry id"""
        db_entry = (
            self.session.execute(
                select(RegistryEntry).where(RegistryEntry.id == entry_id)
            )
            .scalars()
            .one()
        )
        if db_entry is None or not db_entry.is_active:
            raise errors.RegistryEntryNotFoundError(entry_id=entry_id)
        try:
            entry_obj = RegistryRecord(
                id=db_entry.id,
                run_id=db_entry.run_id,
                phase=db_entry.phase,
                content_format=db_entry.content_format,
                strategy_name=db_entry.strategy_name,
                content_hash=db_entry.content_hash,
                address=db_entry.payload_address,
                created_at=db_entry.created_at,
                is_active=db_entry.is_active,
            )
        except ValidationError as e:
            raise errors.InvalidRegistryEntryError(entry_id=entry_id) from e
        return entry_obj

    def get_entry_by_run_id(self, *, run_id: int, phase: Phase) -> RegistryRecord:
        """Retreives entry object by run_id and phase"""
        try:
            db_entry = (
                self.session.execute(
                    select(RegistryEntry).where(
                        RegistryEntry.run_id == run_id, RegistryEntry.phase == phase
                    )
                )
                .scalars()
                .one()
            )
        except NoResultFound as e:
            raise errors.RegistryEntryNotFoundError(run_id=run_id, phase=phase) from e
        if not db_entry.is_active:
            raise errors.RegistryEntryNotFoundError(run_id=run_id, phase=phase)
        try:
            entry_obj = RegistryRecord(
                id=db_entry.id,
                run_id=db_entry.run_id,
                phase=db_entry.phase,
                content_format=db_entry.content_format,
                strategy_name=db_entry.strategy_name,
                content_hash=db_entry.content_hash,
                address=db_entry.payload_address,
                created_at=db_entry.created_at,
                is_active=db_entry.is_active,
            )
        except ValidationError as e:
            raise errors.InvalidRegistryEntryError(run_id=run_id, phase=phase) from e
        return entry_obj

    def get_entry_by_hash(self, *, content_hash: str) -> RegistryRecord:
        """Retreives entry object by content hash"""
        try:
            db_entry = (
                self.session.execute(
                    select(RegistryEntry).where(
                        RegistryEntry.content_hash == content_hash
                    )
                )
                .scalars()
                .one()
            )
        except NoResultFound as e:
            raise errors.RegistryEntryNotFoundError(content_hash=content_hash) from e
        if not db_entry.is_active:
            raise errors.RegistryEntryNotFoundError(content_hash=content_hash)
        try:
            entry_obj = RegistryRecord(
                id=db_entry.id,
                run_id=db_entry.run_id,
                phase=db_entry.phase,
                content_format=db_entry.content_format,
                strategy_name=db_entry.strategy_name,
                content_hash=db_entry.content_hash,
                address=db_entry.payload_address,
                created_at=db_entry.created_at,
                is_active=db_entry.is_active,
            )
        except ValidationError as e:
            raise errors.InvalidRegistryEntryError(content_hash=content_hash) from e
        return entry_obj


class PayloadStoreSQLite:
    def __init__(self, session: Session):
        self.session = session

    def save(self, *, phase: Phase, payload: bytes) -> str:
        record = PayloadRecord(phase=phase, payload=payload)
        self.session.add(record)
        self.session.commit()
        return str(record.id)

    def load(self, *, address: str) -> bytes:
        try:
            numeric_address = int(address)
        except ValueError as e:
            raise errors.SerializationError(
                f"Argument 'address' of {self.__class__.__name__}"
                f"load() method could not be serialized into int type."
            ) from e

        record = self.session.get(PayloadRecord, numeric_address)
        if record is None or not record.is_active:
            raise errors.PayloadNotFoundError(
                f"No active payload at address {numeric_address}"
            )
        return record.payload
