from typing import Self

from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session

from fluxus.models.orm import FluxusORM
from fluxus.settings import RUNTIME_STORE
from fluxus.storage.backend import (
    FetchCacheStore,
    PayloadStore,
    PipelineRunRecords,
    RegistryStore,
)


class UnitOfWork:
    def __init__(self, engine: Engine | None = None):
        self.engine = engine or create_engine(RUNTIME_STORE)
        FluxusORM.metadata.create_all(self.engine, checkfirst=True)
        self.connection = self.engine.connect()
        self.pipeline_session = Session(bind=self.engine)
        self.run_records_session = Session(bind=self.engine)
        self._run_records_store = PipelineRunRecords(session=self.run_records_session)
        self._payload_store = PayloadStore(session=self.pipeline_session)
        self._registry_store = RegistryStore(session=self.pipeline_session)
        self._fetch_cache_store = FetchCacheStore(session=self.pipeline_session)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            self.rollback()
        self.pipeline_session.close()
        self.run_records_session.close()

    @property
    def run_records_store(self) -> PipelineRunRecords:
        return self._run_records_store

    @property
    def payload_store(self) -> PayloadStore:
        return self._payload_store

    @property
    def registry_store(self) -> RegistryStore:
        return self._registry_store

    @property
    def fetch_cache_store(self) -> FetchCacheStore:
        return self._fetch_cache_store

    def commit(self) -> None:
        self.pipeline_session.commit()

    def rollback(self) -> None:
        self.pipeline_session.rollback()
