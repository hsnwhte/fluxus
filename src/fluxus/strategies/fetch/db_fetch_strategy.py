import json
from sqlalchemy import Table, MetaData, select, create_engine
from sqlalchemy.exc import ArgumentError, OperationalError
from sqlalchemy.orm import Session
from fluxus.strategies.protocols import FetchStrategyProtocol
from fluxus.exceptions import errors
from fluxus.enums import ExtractableFormat
from fluxus.models.dto import ExtractableData

class DBFetchStrategy:
    @staticmethod
    def fetch(*, address:str, table_name:str|None=None)-> ExtractableData:
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
        except OperationalError as e:
            raise errors.FetchTableNotFoundError(table_name) from e

        try:
            content = json.dumps([dict(row) for row in rows]).encode()
            return ExtractableData(content=content, format=ExtractableFormat.JSON)

        except TypeError as e:
            raise errors.FetchTableSerializationError(table_name) from e