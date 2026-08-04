import pytest
import json
from pathlib import Path
from sqlalchemy import create_engine, Engine, text

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.strategies.fetch.db_fetch_strategy import DBFetchStrategy


@pytest.fixture
def temp_address(tmp_path: Path):
    temp_path = tmp_path / "test_source.sqlite"
    return f"sqlite:///{temp_path}"


@pytest.fixture
def test_kwargs():
    return [
        {"id": 1, "test_data": "This is the first test sentence."},
        {"id": 2, "test_data": "This is the second test sentence."},
    ]


@pytest.fixture
def test_source(temp_address: str, test_kwargs: dict):
    test_engine: Engine = create_engine(temp_address)
    stmt = text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, test_data TEXT)")
    with test_engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    stmt = text("INSERT INTO test_table (id, test_data) VALUES (:id, :test_data)")
    with test_engine.connect() as conn:
        for row in test_kwargs:
            conn.execute(stmt, row)
        conn.commit()


def test_db_fetch_strategy_success(
    temp_address: str, test_kwargs: list, test_source: None
):
    fetched_data = DBFetchStrategy.fetch(address=temp_address, table_name="test_table")

    parsed = json.loads(fetched_data.content)
    assert parsed == test_kwargs
    assert fetched_data.source_format == ContentFormat.JSON


def test_db_fetch_strategy_invalid_url(temp_address: str):
    temp_address: str = "wrong_address"

    with pytest.raises(errors.FetchDbUrlNotFoundError):
        DBFetchStrategy.fetch(address=temp_address, table_name="test_table")


def test_db_fetch_strategy_table_not_found(temp_address: str):
    with pytest.raises(errors.FetchTableNotFoundError):
        DBFetchStrategy.fetch(address=temp_address, table_name="invalid_table_name")


def test_db_fetch_strategy_table_name_not_provided(temp_address: str):
    with pytest.raises(errors.FetchTableNameNotProvidedError):
        DBFetchStrategy.fetch(address=temp_address, table_name=None)
