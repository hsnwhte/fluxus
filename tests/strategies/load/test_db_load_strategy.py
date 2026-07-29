import pytest
from pathlib import Path
from sqlalchemy import create_engine, text
from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformedData
from fluxus.strategies.load.db_load_strategy import DBLoadStrategy


@pytest.fixture
def target_address(tmp_path:Path):
    db_path = tmp_path / "target.sqlite"
    return f"sqlite:///{db_path}"


@pytest.fixture
def target_table(target_address:str):
    engine = create_engine(target_address)
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, test_data TEXT)"))
        conn.commit()
    return engine


def test_db_load_strategy_success(target_address:str, target_table:Engine):
    rows = [{"id": 1, "test_data": "first"}, {"id": 2, "test_data": "second"}]
    data = TransformedData(content=__import__("json").dumps(rows).encode())

    DBLoadStrategy.load(data=data, address=target_address, target_format=ContentFormat.JSON, table_name="test_table")

    with target_table.connect() as conn:
        result = conn.execute(text("SELECT id, test_data FROM test_table ORDER BY id")).fetchall()
    assert [dict(r._mapping) for r in result] == rows


def test_db_load_strategy_table_name_not_provided(target_address:str):
    data = TransformedData(content=b"[]")
    with pytest.raises(errors.LoadTableNameNotProvidedError):
        DBLoadStrategy.load(data=data, address=target_address, target_format=ContentFormat.JSON, table_name=None)


def test_db_load_strategy_table_not_found(target_address:str):
    data = TransformedData(content=b"[]")
    with pytest.raises(errors.LoadTableNotFoundError):
        DBLoadStrategy.load(data=data, address=target_address, target_format=ContentFormat.JSON, table_name="nonexistent")