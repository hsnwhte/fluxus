from pathlib import Path

from fluxus.orchestrator import Orchestrator
from fluxus.models.dto import InputArgs
from fluxus.storage.sqlite_backend import PayloadStoreSQLite, RegistryStoreSQLite, PipelineRunRecordsSQLite

from fluxus.enums import FluxusIOType

source_address1=Path(__file__).resolve().parent.parent / "data" / "sample.xml"
source_address2="https://www.legislation.gov.uk/new/data.feed"
source_address3 = f"sqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'source.sqlite'}"
target_address1=Path(__file__).resolve().parent.parent / "data" / "sample_output.bin"


input_args:InputArgs = InputArgs(
    source_type = FluxusIOType.DB,
    source_address = str(source_address3),
    source_table = "test_table",
    target_type = FluxusIOType.FILE,
    target_address = str(target_address1),
    target_table = None
)

orchestrator = Orchestrator(
    input_args = input_args,
    run_records_store=PipelineRunRecordsSQLite(),
    payload_store=PayloadStoreSQLite(),
    registry_store=RegistryStoreSQLite()
)


if __name__ == "__main__":
    orchestrator.run()