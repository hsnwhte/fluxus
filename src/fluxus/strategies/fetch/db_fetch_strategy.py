import json

from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.exc import ArgumentError, NoSuchTableError, OperationalError
from sqlalchemy.orm import Session

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData


class DBFetchStrategy:
    @staticmethod
    def fetch(*, address: str, table_name: str | None = None) -> ExtractableData:
        if table_name is None:
            raise errors.FetchTableNameNotProvidedError()
        try:
            engine = create_engine(address)
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            session = Session(bind=engine)
            rows = session.execute(select(table)).mappings().all()
        except ArgumentError as e:
            raise errors.FetchDbUrlNotFoundError(address) from e
        except (OperationalError, NoSuchTableError) as e:
            raise errors.FetchTableNotFoundError(table_name) from e

        try:
            content = json.dumps([dict(row) for row in rows]).encode()
            return ExtractableData(content=content, source_format=ContentFormat.JSON)

        except TypeError as e:
            raise errors.FetchTableSerializationError(table_name) from e
