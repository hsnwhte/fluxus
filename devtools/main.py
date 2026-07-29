import logging
import typer
from pydantic import ValidationInfo, ValidationError
from devtools.settings import *
from devtools.tools import db_tools
from fluxus.logging_config import setup_logging
from fluxus.enums import FluxusIOType, ContentFormat
from fluxus.orchestrator import Orchestrator
from fluxus.exceptions import errors

from fluxus.models.dto import InputArgs
from fluxus.storage.sqlite_backend import (
    PipelineRunRecordsSQLite,
    PayloadStoreSQLite,
    RegistryStoreSQLite,
)

logger = logging.getLogger(__name__)

dev = typer.Typer()


@dev.callback()
def callback():
    pass


@dev.command(name="test")
def test(
    debug: bool = typer.Option(False, "--debug", "-d"),
    source_type: FluxusIOType = typer.Option(..., "--source-type", "-soty"),
    source_address: str = typer.Option(..., "--source-address", "-soad"),
    target_type: FluxusIOType = typer.Option(..., "--target-type", "-taty"),
    target_address: str = typer.Option(..., "--target-address", "-taad"),
    transform_strategy_name: str = typer.Option(..., "--transform-strategy", "-tsn"),
    source_table: str = typer.Option(None, "--source-table", "-sota"),
    target_table: str = typer.Option(None, "--target-table", "-tata"),
    target_format: ContentFormat = typer.Option(
        ContentFormat.JSON, "--target-format", "-tafo"
    ),
):
    setup_logging(debug=debug)
    try:
        input_args = InputArgs(
            source_type=source_type,
            source_address=source_address,
            source_table=source_table,
            target_type=target_type,
            target_address=target_address,
            target_table=target_table,
            target_format=target_format,
            transform_strategy_name=transform_strategy_name,
        )
    except ValidationError as e:
        logger.exception(f"Invalid input: {e}")
        typer.echo(f"Invalid input: {e}", err=True)
        raise typer.Exit(code=1)

    eng_pipe = db_tools.get_engine(url=DEV_PIPELINE_DB_URL, echo=True)
    sess_pipe = db_tools.get_session(engine=eng_pipe)
    logger.debug("Pipeline db session created.")

    orchestrator = Orchestrator(
        input_args=input_args,
        run_records_store=PipelineRunRecordsSQLite(session=sess_pipe),
        payload_store=PayloadStoreSQLite(session=sess_pipe),
        registry_store=RegistryStoreSQLite(session=sess_pipe),
    )

    logger.info("Pipeline starting...")
    try:
        entry_id = orchestrator.run()
    except errors.FluxusError as e:
        logger.exception(f"Pipeline failed: {e}")
        typer.echo(f"Pipeline failed: {e}", err=True)
        raise typer.Exit(code=1)

    logger.info(f"Pipeline finished successfully, final registry entry id: {entry_id}")
    typer.echo(f"Success. Final registry entry id: {entry_id}")


@dev.command(name="inspect")
def inspect():
    pass


@dev.command(name="setup-test-env")
def setup_test_env():
    eng_pipe = db_tools.get_engine(url=DEV_PIPELINE_DB_URL, echo=True)
    db_tools.create_all_pipeline_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=DEV_SOURCE_DB_URL, echo=True)
    db_tools.create_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=DEV_TARGET_DB_URL, echo=True)
    db_tools.create_all_target_tables(engine=eng_trg)


@dev.command(name="reset-test-env")
def reset_test_env():
    pass


@dev.command(name="reset-db")
def reset_db():
    pass


if __name__ == "__main__":
    dev()
