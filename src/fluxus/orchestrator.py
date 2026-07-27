from fluxus.models.dto import InputArgs
from fluxus.models.orm import RegistryEntry, PayloadRecord
from fluxus.selector import selector
from fluxus.storage.backend import PayloadStoreProtocol, RegistryStoreProtocol, PipelineRunRecordsProtocol
from fluxus.processors.fetcher import Fetcher
from fluxus.processors.decoder import Decoder
from fluxus.enums import Phase
from fluxus import helpers


class Orchestrator:
    def __init__(
            self,
            input_args:InputArgs,
            run_records_store:PipelineRunRecordsProtocol,
            payload_store:PayloadStoreProtocol,
            registry_store:RegistryStoreProtocol
    ):
        self.input_args = input_args
        self.run_records_store=run_records_store
        self.payload_store=payload_store
        self.registry_store=registry_store

    def run(self):
        run_id: int = self.run_records_store.register_run()

        ### --- 1-A) FETCH PHASE
        if self.input_args.source_type.value in ("api", "db"):
            fetch_strategy = selector.get_fetch_strategy(self.input_args.source_type)
            fetcher=Fetcher(source_address=self.input_args.source_address, strategy=fetch_strategy)
            data = fetcher.fetch()
            payload_address = self.payload_store.save(
                phase=Phase.FETCH,
                payload=data.content
            )
            registered_fetch_data = self.registry_store.save_entry(
                run_id=run_id,
                phase=Phase.FETCH,
                strategy_name=fetch_strategy.__name__,
                content_hash=helpers.generate_hash(content=data.content),
                address=str(payload_address),
            )

        ### --- 1-B) DECODE PHASE
        if self.input_args.source_type.value == "file":
            decode_strategy = selector.get_decode_strategy(self.input_args.source_as_path)
            decoder=Decoder(source_address=self.input_args.source_as_path, strategy=decode_strategy)
            data = decoder.decode()
            payload_address=self.payload_store.save(
                phase=Phase.DECODE,
                payload=data.content
            )
            registered_decode_data = self.registry_store.save_entry(
                run_id=run_id,
                phase=Phase.DECODE,
                strategy_name=decode_strategy.__name__,
                content_hash=helpers.generate_hash(content=data.content),
                address=str(payload_address)
            )

        ### --- 2) EXTRACT PHASE