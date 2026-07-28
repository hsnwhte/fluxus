import json
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.exc import ArgumentError, OperationalError, NoSuchTableError
from sqlalchemy.orm import Session
from fluxus.exceptions import errors
from fluxus.models.dto import TransformedData

class DBLoadStrategy:
    @staticmethod
    def load(*, data:TransformedData, address:str, table_name:str|None=None) -> None:
        if table_name is None:
            raise errors.LoadTableNameNotProvidedError()

        rows = json.loads(data.content)

        try:
            engine = create_engine(address)
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
        except ArgumentError as e:
            raise errors.LoadDbUrlNotFoundError(address) from e
        except (OperationalError, NoSuchTableError) as e:
            raise errors.LoadTableNotFoundError(table_name) from e

        with Session(bind=engine) as session:
            session.execute(table.insert(), rows)
            session.commit()