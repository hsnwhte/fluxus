import logging
import typer
from pydantic import ValidationError
from dataclasses import asdict
from devtools.settings import *
from devtools.tools import db_tools
from devtools.test_packages import TEST_PACKAGES
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
    inject_test_pack: int = typer.Option(None, "--test-pack", "-i"),
    source_type: FluxusIOType = typer.Option(None, "--source-type", "-soty"),
    source_address: str = typer.Option(None, "--source-address", "-soad"),
    target_type: FluxusIOType = typer.Option(None, "--target-type", "-taty"),
    target_address: str = typer.Option(None, "--target-address", "-taad"),
    transform_strategy_name: str = typer.Option(None, "--transform-strategy", "-tsn"),
    source_table: str = typer.Option(None, "--source-table", "-sota"),
    target_table: str = typer.Option(None, "--target-table", "-tata"),
    target_format: ContentFormat = typer.Option(
        ContentFormat.JSON, "--target-format", "-tafo"
    ),
):
    setup_logging(debug=debug)
    if inject_test_pack:
        try:
            pack = TEST_PACKAGES.get(inject_test_pack, None)
            if pack is None:
                typer.echo(
                    f"Test package '{inject_test_pack}' could not be found.", err=True
                )
                raise typer.Exit(code=1)
            input_args = InputArgs(**asdict(pack))
        except ValidationError as e:
            logger.exception(f"Invalid input: {e}")
            typer.echo(f"Invalid input: {e}", err=True)
            raise typer.Exit(code=1)
    else:
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


@dev.command(name="soft-reset-test-env")
def reset_test_env():
    eng_pipe = db_tools.get_engine(url=DEV_PIPELINE_DB_URL, echo=True)
    db_tools.reset_all_pipeline_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=DEV_SOURCE_DB_URL, echo=True)
    db_tools.reset_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=DEV_TARGET_DB_URL, echo=True)
    db_tools.reset_all_target_tables(engine=eng_trg)


@dev.command(name="hard-reset-test-env")
def hard_reset_test_env():
    eng_pipe = db_tools.get_engine(url=DEV_PIPELINE_DB_URL, echo=True)
    db_tools.drop_all_pipeline_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=DEV_SOURCE_DB_URL, echo=True)
    db_tools.drop_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=DEV_TARGET_DB_URL, echo=True)
    db_tools.drop_all_target_tables(engine=eng_trg)


if __name__ == "__main__":
    dev()
