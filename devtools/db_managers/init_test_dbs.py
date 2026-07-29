from pathlib import Path
from sqlalchemy import create_engine

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_SOURCE_DB_PATH = _PROJECT_ROOT / "data" / "source.sqlite"
_SOURCE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
SOURCE_STORE_ADDRESS = f"sqlite:///{_SOURCE_DB_PATH}"

_TARGET_DB_PATH = _PROJECT_ROOT / "data" / "target.sqlite"
_TARGET_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
TARGET_STORE_ADDRESS = f"sqlite:///{_TARGET_DB_PATH}"


source_engine = create_engine(SOURCE_STORE_ADDRESS)
target_engine = create_engine(TARGET_STORE_ADDRESS)


def _init_target_db():
    from sqlalchemy import text
    with target_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                test_data TEXT
            )
        """))
        conn.commit()

def _init_source_db():
    from sqlalchemy import text
    with source_engine.connect() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS test_table
                          (
                              id
                              INTEGER
                              PRIMARY
                              KEY,
                              test_data
                              TEXT
                          )
                          """))
        conn.execute(text("""
                          INSERT INTO test_table (id, test_data)
                          VALUES (1, 'This is a test sentence.')
                          """))
        conn.commit()

if __name__ == "__main__":
    _init_target_db()


