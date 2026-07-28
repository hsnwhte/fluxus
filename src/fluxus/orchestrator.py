from fluxus import settings
from fluxus.models.dto import InputArgs, ExtractableData, TransformableData
from fluxus.selector import selector
from fluxus.storage.backend import PayloadStoreProtocol, RegistryStoreProtocol, PipelineRunRecordsProtocol
from fluxus.processors.fetcher import Fetcher
from fluxus.processors.decoder import Decoder
from fluxus.processors.extractor import Extractor
from fluxus.processors.transformer import Transformer
from fluxus.processors.loader import Loader
from fluxus.enums import Phase, ContentFormat
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

        if self.input_args.source_type.value in ("api", "db"):
            entry_id = self._fetch(run_id)
        if self.input_args.source_type.value == "file":
            entry_id = self._decode(run_id)
        self._extract(entry_id)


    def _fetch(self, run_id:int) -> int:
        fetch_strategy = selector.get_fetch_strategy(self.input_args.source_type)
        fetcher=Fetcher(source_address=self.input_args.source_address, strategy=fetch_strategy, table_name = self.input_args.source_table)
        data = fetcher.fetch()
        payload_address = self.payload_store.save(
            phase=Phase.FETCH,
            payload=data.content
        )

        entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.FETCH,
            content_format=data.source_format,
            strategy_name=fetch_strategy.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address),
        )
        return entry_id

    def _decode(self, run_id:int) -> int:
        decode_strategy = selector.get_decode_strategy(self.input_args.source_as_path)
        decoder=Decoder(source_address=self.input_args.source_as_path, strategy=decode_strategy)
        data = decoder.decode()
        payload_address=self.payload_store.save(
            phase=Phase.DECODE,
            payload=data.content
        )

        entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.DECODE,
            content_format=data.source_format,
            strategy_name=decode_strategy.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address)
        )
        return entry_id

    def _extract(self, run_id:int, entry_id:int) -> int:
        entry = self.registry_store.get_entry_by_id(entry_id=entry_id)
        extract_strategy = selector.get_extract_strategy(entry.content_format)
        content_bytes=self.payload_store.load(address=entry.address)
        extractor=Extractor(content=content_bytes, strategy=extract_strategy)
        data = extractor.extract()

        payload_address = self.payload_store.save(
            phase=Phase.EXTRACT,
            payload=data.content
        )

        entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.EXTRACT,
            content_format=settings.NORMALIZED_FORMAT,
            strategy_name=extract_strategy.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address)
        )
        return entry_id