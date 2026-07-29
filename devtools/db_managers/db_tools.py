from sqlalchemy import text
from sqlalchemy.engine import Engine

def reset_table(engine: Engine, table_name: str) -> None:
    with engine.connect() as conn:
        conn.execute(text(f"DELETE FROM {table_name}"))
        conn.execute(text("DELETE FROM sqlite_sequence WHERE name = :table_name"), {"table_name": table_name})
        conn.commit()


def drop_table(engine: Engine, table_name: str) -> None:
    """Drops the given table entirely (schema and data).
    Use init_pipeline_db.py / init_test_dbs.py afterwards to recreate it.
    """
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        conn.commit()



if __name__ == "__main__":
    from sqlalchemy import create_engine
    from fluxus.settings import PIPELINE_STORE_ADDRESS
    from init_test_dbs import SOURCE_STORE_ADDRESS, TARGET_STORE_ADDRESS

    pipeline_engine = create_engine(PIPELINE_STORE_ADDRESS)
    drop_table(pipeline_engine, "registry")
    drop_table(pipeline_engine, "payloads")
    drop_table(pipeline_engine, "pipeline_runs")

    source_engine = create_engine(SOURCE_STORE_ADDRESS)
    drop_table(source_engine, "test_table")