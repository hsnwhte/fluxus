from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session
from fluxus.models.orm import FluxusORM
from devtools.tools.dev_orm import FluxusDevSourceORM, FluxusDevTargetORM


def get_engine(*, url: str, echo: bool = False) -> Engine:
    return create_engine(url=url, echo=echo)


def get_session(*, engine: Engine) -> Session:
    return Session(bind=engine)


def create_all_runtime_tables(*, engine: Engine) -> None:
    FluxusORM.metadata.create_all(engine)


def reset_all_runtime_tables(*, engine: Engine) -> None:
    for table_name in FluxusORM.metadata.tables.keys():
        reset_table(engine=engine, table_name=table_name)


def drop_all_runtime_tables(*, engine: Engine) -> None:
    for table_name in FluxusORM.metadata.tables.keys():
        drop_table(engine=engine, table_name=table_name)


def create_all_source_tables(*, engine: Engine) -> None:
    FluxusDevSourceORM.metadata.create_all(engine)


def reset_all_source_tables(*, engine: Engine) -> None:
    for table_name in FluxusDevSourceORM.metadata.tables.keys():
        reset_table(engine=engine, table_name=table_name)


def drop_all_source_tables(*, engine: Engine) -> None:
    for table_name in FluxusDevSourceORM.metadata.tables.keys():
        drop_table(engine=engine, table_name=table_name)


def create_all_target_tables(*, engine: Engine) -> None:
    FluxusDevTargetORM.metadata.create_all(engine)


def reset_all_target_tables(*, engine: Engine) -> None:
    for table_name in FluxusDevTargetORM.metadata.tables.keys():
        reset_table(engine=engine, table_name=table_name)


def drop_all_target_tables(*, engine: Engine) -> None:
    for table_name in FluxusDevTargetORM.metadata.tables.keys():
        drop_table(engine=engine, table_name=table_name)


def command_database(
    *, engine: Engine, stmt1: str, stmt2: str | None = None, stmt3: str | None = None
):
    with engine.connect() as conn:
        conn.execute(text(stmt1))
        if stmt2:
            conn.execute(text(stmt2))
        if stmt3:
            conn.execute(text(stmt3))
        conn.commit()


def reset_table(*, engine: Engine, table_name: str) -> None:
    dialect = engine.dialect.name
    with engine.connect() as conn:
        if dialect == "postgresql":
            conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        else:
            conn.execute(text(f"DELETE FROM {table_name}"))
            try:
                conn.execute(
                    text("DELETE FROM sqlite_sequence WHERE name = :table_name"),
                    {"table_name": table_name},
                )
            except (OperationalError, ProgrammingError):
                pass
        conn.commit()


def drop_table(*, engine: Engine, table_name: str) -> None:
    dialect = engine.dialect.name
    with engine.connect() as conn:
        if dialect == "postgresql":
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        else:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            try:
                conn.execute(
                    text("DELETE FROM sqlite_sequence WHERE name = :table_name"),
                    {"table_name": table_name},
                )
            except (OperationalError, ProgrammingError):
                pass
        conn.commit()
