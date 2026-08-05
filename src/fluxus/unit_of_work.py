from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import Session
from fluxus.settings import RUNTIME_STORE
from fluxus.storage.backend_protocols import (
    PipelineRunRecordsProtocol,
    PayloadStoreProtocol,
    RegistryStoreProtocol,
    FetchCacheStoreProtocol,
)
from fluxus.storage.backend import (
    PipelineRunRecords,
    PayloadStore,
    RegistryStore,
    FetchCacheStore,
)


class UnitOfWork:
    def __init__(self, engine: Engine | None = None):
        self.engine = engine or create_engine(RUNTIME_STORE)
        self.pipeline_session = self._get_session(self.engine)
        self.run_records_session = self._get_session(self.engine)
        self._run_records_store = PipelineRunRecords(session=self.run_records_session)
        self._payload_store = PayloadStore(session=self.pipeline_session)
        self._registry_store = RegistryStore(session=self.pipeline_session)
        self._fetch_cache_store = FetchCacheStore(session=self.pipeline_session)

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            self.rollback()
        self.pipeline_session.close()
        self.run_records_session.close()

    @property
    def run_records_store(self) -> PipelineRunRecordsProtocol:
        return self._run_records_store

    @property
    def payload_store(self) -> PayloadStoreProtocol:
        return self._payload_store

    @property
    def registry_store(self) -> RegistryStoreProtocol:
        return self._registry_store

    @property
    def fetch_cache_store(self) -> FetchCacheStoreProtocol:
        return self._fetch_cache_store

    def commit(self) -> None:
        self.pipeline_session.commit()

    def rollback(self) -> None:
        self.pipeline_session.rollback()

    @staticmethod
    def _get_session(engine: Engine) -> Session:
        return Session(bind=engine)
