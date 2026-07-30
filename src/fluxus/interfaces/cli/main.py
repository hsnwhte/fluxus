import logging
import typer
from pathlib import Path
from pydantic import ValidationError

from fluxus.logging_config import setup_logging
from fluxus.enums import FluxusIOType, ContentFormat
from fluxus.db_session_factory import create_pipeline_store_session
from fluxus.orchestrator import Orchestrator
from fluxus.exceptions import errors
from fluxus.strategies.transform import transform_installer
from fluxus.strategies.transform import TRANSFORM_STRATEGY_MAP
from fluxus.models.dto import InputArgs
from fluxus.storage.sqlite_backend import (
    PipelineRunRecordsSQLite,
    PayloadStoreSQLite,
    RegistryStoreSQLite,
)

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.callback()
def callback(debug: bool = typer.Option(False, "--debug", "-d")):
    setup_logging(debug=debug)


@app.command(name="run")
def run(
    source_type: FluxusIOType = typer.Option(..., "--source-type", "-soty"),
    source_address: str = typer.Option(..., "--source-address", "-soad"),
    target_type: FluxusIOType = typer.Option(..., "--target-type", "-taty"),
    target_address: str = typer.Option(..., "--target-address", "-taad"),
    transform_strategy_id: int = typer.Option(..., "--transform-strategy", "-tsi"),
    source_table: str = typer.Option(None, "--source-table", "-sota"),
    target_table: str = typer.Option(None, "--target-table", "-tata"),
    target_format: ContentFormat = typer.Option(
        ContentFormat.JSON, "--target-format", "-tafo"
    ),
):

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

    session = create_pipeline_store_session()
    logger.debug("Pipeline db session created.")

    orchestrator = Orchestrator(
        input_args=input_args,
        run_records_store=PipelineRunRecordsSQLite(session=session),
        payload_store=PayloadStoreSQLite(session=session),
        registry_store=RegistryStoreSQLite(session=session),
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


@app.command(name="install-strategy")
def install_strategy_command(
    strategy_path: Path = typer.Option(..., "--path", "-p"),
):
    try:
        new_id = transform_installer.install_strategy(strategy_path=strategy_path)
    except errors.FluxusError as e:
        logger.exception(f"Strategy install failed: {e}")
        typer.echo(f"Install failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy installed successfully with id: {new_id}")


@app.command(name="uninstall-strategy")
def uninstall_strategy_command(
    strategy_id: int = typer.Option(..., "--id", "-i"),
):
    try:
        transform_installer.uninstall_strategy(strategy_id=strategy_id)
    except errors.FluxusError as e:
        logger.exception(f"Strategy uninstall failed: {e}")
        typer.echo(f"Uninstall failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy {strategy_id} uninstalled successfully.")


@app.command(name="show-strategies")
def show_strategies():
    for strategy_id, strategy_class in sorted(TRANSFORM_STRATEGY_MAP.items()):
        marker = " (default, cannot uninstall)" if strategy_id == 0 else ""
        typer.echo(f"{strategy_id}: {strategy_class.__name__}{marker}")
