from fluxus.models.dto import InputArgs
from fluxus.models.orm import RegistryEntry, PayloadRecord
from fluxus.selector import selector
from fluxus.storage.sqlite_backend import PipelineRunRecordsSQLite, PayloadStoreSQLite
from fluxus.processors.fetcher import Fetcher
from fluxus.processors.decoder import Decoder
from fluxus.enums import Phase
from fluxus import helpers


class Orchestrator:
    def __init__(self, input_args:InputArgs):
        self.input_args = input_args

    def run(self):
        records = PipelineRunRecordsSQLite()
        run_id: int = records.register_run()

        if self.input_args.source_type.value in ("api", "db"):
            fetch_strategy = selector.get_fetch_strategy(self.input_args.source_type)
            fetcher=Fetcher(source_address=self.input_args.source_address, strategy=fetch_strategy)
            data = fetcher.fetch()

            store = PayloadStoreSQLite()
            payload_address = store.save(phase=Phase.FETCH, payload=data.content)



        if self.input_args.source_type.value == "file":
            decode_strategy = selector.get_decode_strategy(self.source_type)

