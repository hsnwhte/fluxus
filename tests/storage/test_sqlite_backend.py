import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from fluxus.helpers import generate_hash
from fluxus.enums import Phase, ContentFormat
from fluxus.models.orm import FluxusORM
from fluxus.storage.sqlite_backend import PipelineRunRecordsSQLite, RegistryStoreSQLite, PayloadStoreSQLite



@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    FluxusORM.metadata.create_all(engine)
    return engine

@pytest.fixture
def registry_entry_kwargs():
    return {
        "run_id": 1,
        "phase": Phase.FETCH,
        "content_format": ContentFormat.JSON,
        "strategy_name": "db_fetch_strategy",
        "content_hash": generate_hash(content="test".encode()),
        "address": "1",
    }

@pytest.fixture
def registry_store(test_engine: Engine):
    session = Session(bind=test_engine)
    return RegistryStoreSQLite(session=session)

@pytest.fixture
def saved_registry_entry(
    registry_store: RegistryStoreSQLite,
    registry_entry_kwargs: dict):
    entry_id = registry_store.save_entry(**registry_entry_kwargs)
    return entry_id, registry_entry_kwargs

@pytest.fixture
def payload_store(test_engine:Engine):
    session=Session(bind=test_engine)
    return PayloadStoreSQLite(session=session)


def test_pipeline_run_records_register_run(test_engine:Engine):
    session = Session(bind=test_engine)
    store = PipelineRunRecordsSQLite(session=session)

    run_id = store.register_run()

    assert isinstance(run_id, int)
    assert run_id == 1

def test_registry_store_save_entry(test_engine:Engine, registry_entry_kwargs:dict):
    session = Session(bind=test_engine)
    store = RegistryStoreSQLite(session=session)

    entry_id = store.save_entry(**registry_entry_kwargs)

    assert isinstance(entry_id, int)
    assert entry_id == 1

def test_registry_store_get_entry_by_id(
        test_engine:Engine,
        saved_registry_entry:tuple[int, dict],
        registry_store: RegistryStoreSQLite
):
    entry_id, kwargs = saved_registry_entry

    data = registry_store.get_entry_by_id(entry_id=entry_id)

    #Assert
    assert data.id == 1
    assert data.run_id == kwargs["run_id"]
    assert data.phase == kwargs["phase"]
    assert data.content_format == kwargs["content_format"]
    assert data.strategy_name == kwargs["strategy_name"]
    assert data.content_hash == kwargs["content_hash"]
    assert data.address == kwargs["address"]


def test_registry_store_get_entry_by_run_id(
        test_engine: Engine,
        saved_registry_entry: tuple[int, dict],
        registry_store: RegistryStoreSQLite
):
    entry_id, kwargs = saved_registry_entry

    data = registry_store.get_entry_by_run_id(run_id=kwargs["run_id"], phase=kwargs["phase"])

    # Assert
    assert data.id == entry_id
    assert data.run_id == kwargs["run_id"]
    assert data.phase == kwargs["phase"]
    assert data.strategy_name == kwargs["strategy_name"]
    assert data.content_hash == kwargs["content_hash"]
    assert data.address == kwargs["address"]

def test_registry_store_get_entry_by_content_hash(
        test_engine: Engine,
        saved_registry_entry: tuple[int, dict],
        registry_store: RegistryStoreSQLite
):
    entry_id, kwargs = saved_registry_entry

    data = registry_store.get_entry_by_hash(content_hash=kwargs["content_hash"])

    # Assert
    assert data.id == entry_id
    assert data.run_id == kwargs["run_id"]
    assert data.phase == kwargs["phase"]
    assert data.strategy_name == kwargs["strategy_name"]
    assert data.content_hash == kwargs["content_hash"]
    assert data.address == kwargs["address"]


def test_payload_store_save(test_engine:Engine, payload_store:PayloadStoreSQLite):
    phase=Phase.FETCH
    payload="test".encode()

    record_id_str = payload_store.save(phase=phase, payload=payload)

    assert isinstance(record_id_str, str)
    assert record_id_str == "1"


def test_payload_store_load(test_engine: Engine, payload_store: PayloadStoreSQLite):
    phase = Phase.FETCH
    payload = "test".encode()
    payload_store.save(phase=phase, payload=payload)

    payload = payload_store.load(address="1")

    assert isinstance(payload, bytes)
    assert payload == "test".encode()