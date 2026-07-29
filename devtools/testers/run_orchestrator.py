from pathlib import Path

from fluxus.orchestrator import Orchestrator
from fluxus.models.dto import InputArgs
from fluxus.storage.sqlite_backend import PayloadStoreSQLite, RegistryStoreSQLite, PipelineRunRecordsSQLite
from fluxus import db_session_factory
from fluxus.enums import FluxusIOType, ContentFormat

source_address1=Path(__file__).resolve().parent.parent.parent / "data" / "sample.xml"
source_address2="https://jsonplaceholder.typicode.com/todos/1"
source_address3 = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'source.sqlite'}"
target_address1=Path(__file__).resolve().parent.parent.parent / "data" / "sample_output.bin"
target_address2 = "https://jsonplaceholder.typicode.com/posts/1"
target_address3 = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'target.sqlite'}"

input_args: InputArgs = InputArgs(
    source_type=FluxusIOType.API,
    source_address=str(source_address2),
    source_table=None,
    target_type=FluxusIOType.FILE,
    target_address=str(target_address1),
    target_table=None,
    target_format=ContentFormat.XML,
    transform_strategy_name="sample_passthrough",
)

session = db_session_factory.create_pipeline_store_session()

orchestrator = Orchestrator(
    input_args=input_args,
    run_records_store=PipelineRunRecordsSQLite(session=session),
    payload_store=PayloadStoreSQLite(session=session),
    registry_store=RegistryStoreSQLite(session=session),
)


if __name__ == "__main__":
    entry_id = orchestrator.run()
    print(f"Pipeline finished. Final registry entry id: {entry_id}")