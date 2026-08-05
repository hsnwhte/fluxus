import logging
import typer
from pathlib import Path
from pydantic import ValidationError

from fluxus.logging_config import setup_logging
from fluxus.enums import FluxusIOType, ContentFormat
from fluxus.unit_of_work import UnitOfWork
from fluxus.orchestrator import Orchestrator
from fluxus.exceptions import errors
from fluxus.strategies.transform import transform_installer
from fluxus.strategies.transform import TRANSFORM_STRATEGY_MAP
from fluxus.models.dto import InputArgs

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
    transform_strategy_uid: str = typer.Option(..., "--transform-strategy", "-tsu"),
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
            transform_strategy_uid=transform_strategy_uid,
        )
    except ValidationError as e:
        logger.exception(f"Invalid input: {e}")
        typer.echo(f"Invalid input: {e}", err=True)
        raise typer.Exit(code=1)

    with UnitOfWork() as uow:
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


@app.command(name="install-strategy")
def install_strategy_command(
    strategy_path: Path = typer.Option(..., "--path", "-p"),
):
    try:
        new_uid = transform_installer.install_strategy(strategy_path=strategy_path)
    except errors.FluxusError as e:
        logger.exception(f"Strategy install failed: {e}")
        typer.echo(f"Install failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy installed successfully with uid: {new_uid}")


@app.command(name="uninstall-strategy")
def uninstall_strategy_command(
    strategy_uid: str = typer.Option(..., "--uid", "-u"),
):
    try:
        transform_installer.uninstall_strategy(uid=strategy_uid)
    except errors.FluxusError as e:
        logger.exception(f"Strategy uninstall failed: {e}")
        typer.echo(f"Uninstall failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy {strategy_uid} uninstalled successfully.")


@app.command(name="show-strategies")
def show_strategies():
    for strategy_uid, strategy_class in sorted(TRANSFORM_STRATEGY_MAP.items()):
        marker = " (default, cannot uninstall)" if strategy_uid == "default" else ""
        typer.echo(f"{strategy_uid}: {strategy_class.__name__}{marker}")
