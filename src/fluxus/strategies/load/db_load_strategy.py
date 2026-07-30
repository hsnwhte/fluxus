import json
import logging
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.exc import ArgumentError, OperationalError, NoSuchTableError
from sqlalchemy.orm import Session
from fluxus.exceptions import errors
from fluxus.models.dto import TransformedData
from fluxus.enums import ContentFormat

logger = logging.getLogger(__name__)


class DBLoadStrategy:
    @staticmethod
    def load(
        *,
        data: TransformedData,
        address: str,
        target_format: ContentFormat,
        table_name: str | None = None,
    ) -> None:
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
            # EDGE CASE: empty rows list would otherwise produce
            # a single DEFAULT VALUES insert
            if rows:
                session.execute(table.insert(), rows)
            else:
                logger.warning(
                    f"No rows to load into table '{table_name}' — source data was empty."
                )
            session.commit()
