import logging
import typer
import json
from pydantic import ValidationError
from dataclasses import asdict
from devtools import settings as dev_settings
from devtools.tools import db_tools
from devtools.test_packages import TEST_PACKAGES
from fluxus import settings as runtime_settings
from fluxus.logging_config import setup_logging
from fluxus.enums import FluxusIOType, ContentFormat
from fluxus.orchestrator import Orchestrator
from fluxus.exceptions import errors

from fluxus.models.dto import InputArgs
from fluxus.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)
dev = typer.Typer()


@dev.callback()
def callback(debug: bool = typer.Option(False, "--debug", "-d")):
    setup_logging(debug=debug)


@dev.command(name="test")
def test(
    inject_test_pack: int = typer.Option(None, "--test-pack", "-i"),
    source_type: FluxusIOType = typer.Option(None, "--source-type", "-soty"),
    source_address: str = typer.Option(None, "--source-address", "-soad"),
    target_type: FluxusIOType = typer.Option(None, "--target-type", "-taty"),
    target_address: str = typer.Option(None, "--target-address", "-taad"),
    transform_strategy_id: int = typer.Option(None, "--transform-strategy", "-tsn"),
    source_table: str = typer.Option(None, "--source-table", "-sota"),
    target_table: str = typer.Option(None, "--target-table", "-tata"),
    target_format: ContentFormat = typer.Option(
        ContentFormat.JSON, "--target-format", "-tafo"
    ),
):

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
                transform_strategy_id=transform_strategy_id,
            )
        except ValidationError as e:
            logger.exception(f"Invalid input: {e}")
            typer.echo(f"Invalid input: {e}", err=True)
            raise typer.Exit(code=1)

    engine = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=False)
    with UnitOfWork(engine=engine) as uow:
        orchestrator = Orchestrator(input_args=input_args, uow=uow)
        logger.debug("Orchestrator object instantiated")
        logger.info("Pipeline starting...")
        try:
            entry_id = orchestrator.run()
        except errors.FluxusError as e:
            logger.exception(f"Pipeline failed: {e}")
            typer.echo(f"Pipeline failed: {e}", err=True)
            raise typer.Exit(code=1)

        uow.commit()
        logger.info(
            f"Pipeline finished successfully, final registry entry id: {entry_id}"
        )
        typer.echo(f"Success. Final registry entry id: {entry_id}")




@dev.command(name="inspect")
def inspect(
    payload_id: int = typer.Option(..., "--payload-id", "-p"),
):
    engine = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=False)
    with UnitOfWork(engine=engine) as uow:
        try:
            raw_content = uow.payload_store.load(address=str(payload_id))
        except errors.PayloadNotFoundError as e:
            typer.echo(f"Payload not found: {e}", err=True)
            raise typer.Exit(code=1)

        try:
            parsed = json.loads(raw_content)
            typer.echo(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            typer.echo(raw_content.decode(errors="replace"))


@dev.command(name="setup-test-env")
def setup_test_env():
    eng_pipe = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.create_all_runtime_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.create_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.create_all_target_tables(engine=eng_trg)


@dev.command(name="reset-test-env")
def reset_test_env():
    eng_pipe = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.reset_all_runtime_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.reset_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.reset_all_target_tables(engine=eng_trg)


@dev.command(name="hard-reset-test-env")
def hard_reset_test_env():
    eng_pipe = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.drop_all_runtime_tables(engine=eng_pipe)
    eng_src = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.drop_all_source_tables(engine=eng_src)
    eng_trg = db_tools.get_engine(url=dev_settings.DEV_RUNTIME_POSTGRE, echo=True)
    db_tools.drop_all_target_tables(engine=eng_trg)


@dev.command(name="reset-runtime-db")
def reset_runtime_db():
    eng_runtime = db_tools.get_engine(url=runtime_settings.RUNTIME_STORE, echo=True)
    db_tools.reset_all_runtime_tables(engine=eng_runtime)


if __name__ == "__main__":
    dev()
