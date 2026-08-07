import json
import logging
import os
from importlib.metadata import version as lib_version
from pathlib import Path

import typer
from pydantic import ValidationError
from sqlalchemy import text

from fluxus import settings
from fluxus.enums import CliInspectType, CliListType, ContentFormat, FluxusIOType
from fluxus.exceptions import errors
from fluxus.logging_config import setup_logging
from fluxus.models.dto import InputArgs
from fluxus.orchestrator import Orchestrator
from fluxus.strategies.transform import TRANSFORM_STRATEGY_MAP, transform_installer
from fluxus.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.callback()
def callback(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable verbose DEBUG-level logging to a file (logs/fluxus_debug.log).",
    ),
):
    setup_logging(debug=debug)


@app.command(name="run")
def run(
    source_type: FluxusIOType = typer.Option(
        ..., "--source-type", "-sy", help="Type of the data source: file, db, or api."
    ),
    source_address: str = typer.Option(
        ...,
        "--source-address",
        "-sd",
        help="Location of the source: a file path, a DB connection string, or a URL.",
    ),
    target_type: FluxusIOType = typer.Option(
        ..., "--target-type", "-ty", help="Type of the data target: file, db, or api."
    ),
    target_address: str = typer.Option(
        ...,
        "--target-address",
        "-td",
        help="Location of the target: a file path, a DB connection string, or a URL.",
    ),
    transform_strategy_uid: str = typer.Option(
        "default",
        "--transform-strategy",
        "-S",
        help="UID of an installed Transform strategy, or 'default' for the built-in passthrough.",
    ),
    source_table: str = typer.Option(
        None,
        "--source-table",
        "-st",
        help="Table name to read from, required only when source-type is 'db'.",
    ),
    target_table: str = typer.Option(
        None,
        "--target-table",
        "-tt",
        help="Table name to write to, required only when target-type is 'db'.",
    ),
    target_format: ContentFormat = typer.Option(
        ContentFormat.JSON,
        "--target-format",
        "-tf",
        help="Format to write to the target: json, xml, csv, or html.",
    ),
):
    """Run a full ETL pipeline from source to target."""

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
    except (ValidationError, AttributeError) as e:
        logger.error(f"Invalid prompt: {e}")
        typer.echo(f"Invalid input: {e}", err=True)
        raise typer.Exit(code=1)

    orchestrator = Orchestrator(input_args=input_args)
    logger.debug("Orchestrator object instantiated")
    logger.info("Pipeline starting...")
    try:
        entry_id = orchestrator.run()
    except errors.FluxusError as e:
        logger.error(f"Pipeline FAILED: {e}")
        typer.echo(f"Pipeline FAILED: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"SUCCESS. Final registry entry id: {entry_id}")


@app.command(name="show")
def show(
    mode: CliListType = typer.Option(
        CliListType.STRATEGIES,
        "--mode",
        "-m",
        help="What to list: runs (pipeline run history), registry (per-phase entries), or strategies (installed Transform strategies).",
    ),
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of records to show."
    ),
):
    """Show a paginated list of runs, registry entries, or installed strategies."""
    with UnitOfWork() as uow:
        if mode == CliListType.STRATEGIES:
            total = len(TRANSFORM_STRATEGY_MAP)
            typer.echo(f"Total strategies: {total}\n")
            items = sorted(TRANSFORM_STRATEGY_MAP.items())[:limit]
            for uid, cls in items:
                marker = " (default, cannot uninstall)" if uid == "default" else ""
                typer.echo(f"{uid}: {cls.__name__}{marker}")

        elif mode == CliListType.RUNS:
            total = uow.run_records_store.count_runs()
            typer.echo(f"Total runs: {total}\n")
            records = uow.run_records_store.list_runs(limit=limit)
            for r in records:
                typer.echo(
                    f"{r.run_id} | {r.started_at} | {r.status.value} | {r.interrupted_phase.value if r.interrupted_phase else '-'}"
                )
        else:
            total = uow.registry_store.count_entries()
            typer.echo(f"Total registry entries: {total}\n")
            records = uow.registry_store.list_entries(limit=limit)
            for r in records:
                typer.echo(
                    f"{r.id} | run {r.run_id} | {r.phase.value} | {r.strategy_name} | {r.address}"
                )


@app.command(name="inspect")
def inspect(
    record: CliInspectType = typer.Option(
        ...,
        "--record",
        "-r",
        help="What kind of record to inspect: 'registry' for entry metadata, 'payload' for the actual stored content.",
    ),
    entry_id: int = typer.Option(
        ...,
        "--id",
        "-i",
        help="ID of the registry entry (for --record registry) or payload address (for --record payload).",
    ),
):
    """Inspect the metadata of a registry entry or the raw content of a payload."""
    with UnitOfWork() as uow:
        if record == CliInspectType.REGISTRY:
            entry = uow.registry_store.get_entry_by_id(entry_id=entry_id)
            typer.echo(f"Phase: {entry.phase.value}")
            typer.echo(f"Strategy: {entry.strategy_name}")
            typer.echo(f"Address: {entry.address}")
            typer.echo(f"Content hash: {entry.content_hash}")
            typer.echo(f"Created: {entry.created_at}")
        else:
            raw_content = uow.payload_store.load(address=str(entry_id))
            try:
                parsed = json.loads(raw_content)
                typer.echo(json.dumps(parsed, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                typer.echo(raw_content.decode(errors="replace"))


@app.command(name="install-strategy")
def install_strategy(
    strategy_path: Path = typer.Option(
        ...,
        "--path",
        "-p",
        help="Full path to the Transform strategy .py file. Use an absolute path to avoid ambiguity.",
    ),
):
    """Install a Transform strategy from a local .py file."""
    try:
        new_uid = transform_installer.install_strategy(strategy_path=strategy_path)
    except errors.FluxusError as e:
        logger.error(f"Strategy install failed: {e}")
        typer.echo(f"Install failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy installed successfully with uid: {new_uid}")


@app.command(name="uninstall-strategy")
def uninstall_strategy(
    uid: str = typer.Option(
        ...,
        "--uid",
        "-u",
        help="UID of the installed strategy to remove (see 'fluxus show --mode strategies').",
    ),
):
    """Remove an installed Transform strategy by its UID."""
    try:
        transform_installer.uninstall_strategy(uid=uid)
    except errors.FluxusError as e:
        logger.error(f"Strategy uninstall failed: {e}")
        typer.echo(f"Uninstall failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Strategy {uid} uninstalled successfully.")


@app.command(name="version")
def show_version():
    """Print the installed Fluxus version."""
    typer.echo(f"fluxus {lib_version('fluxus')}")


@app.command(name="doctor")
def doctor():
    """Check that the environment, database connection, and directories are healthy."""
    typer.echo("Fluxus health check\n")
    env_path = Path(".env")
    if env_path.exists():
        typer.echo("✓ .env file found")
    else:
        typer.echo("- .env not found (using defaults)")

    try:
        with UnitOfWork() as uow:
            uow.pipeline_session.execute(text("SELECT 1"))
        typer.echo("✓ Database reachable")
    except Exception as e:
        typer.echo(f"✗ Database unreachable: {e}", err=True)

    for path in [settings.LOG_DIR]:
        if path.exists() and os.access(path, os.W_OK):
            typer.echo(f"✓ {path} writable")
        else:
            typer.echo(f"✗ {path} not writable", err=True)
