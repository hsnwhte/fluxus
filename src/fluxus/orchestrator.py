import logging
from fluxus import settings
from fluxus.models.dto import InputArgs, TransformableData, TransformedData
from fluxus.selector import selector
from fluxus.storage.backend import (
    PayloadStoreProtocol,
    RegistryStoreProtocol,
    PipelineRunRecordsProtocol,
)
from fluxus.processors.fetcher import Fetcher
from fluxus.processors.decoder import Decoder
from fluxus.processors.extractor import Extractor
from fluxus.processors.transformer import Transformer
from fluxus.processors.loader import Loader
from fluxus.processors.exporter import Exporter
from fluxus.enums import Phase
from fluxus import helpers
from fluxus.exceptions import errors

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        input_args: InputArgs,
        run_records_store: PipelineRunRecordsProtocol,
        payload_store: PayloadStoreProtocol,
        registry_store: RegistryStoreProtocol,
    ):
        self.input_args = input_args
        self.run_records_store = run_records_store
        self.payload_store = payload_store
        self.registry_store = registry_store

    def run(self) -> int:
        run_id: int = self.run_records_store.register_run()
        logger.info(f"Initiating run: {run_id}")
        if self.input_args.source_type.value in ("api", "db"):
            logger.info(
                f"Fetching from {self.input_args.source_type.value}: '{self.input_args.source_address}'"
            )
            entry_id = self._fetch(run_id)
            logger.info("Fetch successful.")
        elif self.input_args.source_type.value == "file":
            logger.info(
                f"Decoding the {self.input_args.source_type.value}: '{self.input_args.source_address}'"
            )
            entry_id = self._decode(run_id)
            logger.info("Decode successful.")
        else:
            logger.error(f"Failed to fetch/decode the source - invalid args.")
            raise errors.InvalidInputError()

        logger.info("Extracting data...")
        extr_entry_id = self._extract(run_id, entry_id)
        logger.info(f"Extract successful.")

        logger.info(
            f"Transforming data based on strategy: '{self.input_args.transform_strategy_id}'"
        )
        trns_entry_id = self._transform(run_id, extr_entry_id)
        logger.info("Transform successful.")

        if self.input_args.target_type.value in ("api", "db"):
            logger.info(
                f"Loading to {self.input_args.target_type.value}: '{self.input_args.target_address}'"
            )
            load_entry_id = self._load(run_id, trns_entry_id)
            logger.info(f"Load successful. Load Id: {load_entry_id}")
            return load_entry_id

        elif self.input_args.target_type.value == "file":
            logger.info(
                f"Exporting to {self.input_args.target_type.value}: '{self.input_args.target_address}'"
            )
            export_entry_id = self._export(run_id, trns_entry_id)
            logger.info(f"Export successful. Export Id: {export_entry_id}")
            return export_entry_id
        else:
            logger.error(f"Failed to load/export to the source - invalid args.")
            raise errors.InvalidInputError()

    def _export(self, run_id: int, entry_id: int) -> int:
        entry = self.registry_store.get_entry_by_id(entry_id=entry_id)
        content_bytes = self.payload_store.load(address=entry.address)
        transformed_content = TransformedData(content=content_bytes)

        export_strategy = selector.get_export_strategy()
        exporter = Exporter(
            file_path=self.input_args.target_as_path, strategy=export_strategy
        )
        exporter.export(data=transformed_content)

        export_entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.EXPORT,
            content_format=self.input_args.target_format,
            strategy_name=export_strategy.__name__,
            content_hash=helpers.generate_hash(content=content_bytes),
            address=str(self.input_args.target_address),
        )
        return export_entry_id

    def _load(self, run_id: int, entry_id: int) -> int:
        entry = self.registry_store.get_entry_by_id(entry_id=entry_id)
        content_bytes = self.payload_store.load(address=entry.address)
        transformed_content = TransformedData(content=content_bytes)

        load_strategy = selector.get_load_strategy(self.input_args.target_type)
        loader = Loader(
            address=self.input_args.target_address,
            strategy=load_strategy,
            target_format=self.input_args.target_format,
            table_name=self.input_args.target_table,
        )
        loader.load(data=transformed_content)

        load_entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.LOAD,
            content_format=self.input_args.target_format,
            strategy_name=load_strategy.__name__,
            content_hash=helpers.generate_hash(content=content_bytes),
            address=str(self.input_args.target_address),
        )
        return load_entry_id

    def _extract(self, run_id: int, entry_id: int) -> int:
        entry = self.registry_store.get_entry_by_id(entry_id=entry_id)
        extract_strategy = selector.get_extract_strategy(entry.content_format)
        content_bytes = self.payload_store.load(address=entry.address)
        extractor = Extractor(content=content_bytes, strategy=extract_strategy)
        data = extractor.extract()

        payload_address = self.payload_store.save(
            phase=Phase.EXTRACT, payload=data.content
        )

        extr_entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.EXTRACT,
            content_format=settings.NORMALIZED_FORMAT,
            strategy_name=extract_strategy.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address),
        )
        return extr_entry_id

    def _transform(self, run_id: int, entry_id: int) -> int:
        entry = self.registry_store.get_entry_by_id(entry_id=entry_id)
        content_bytes = self.payload_store.load(address=entry.address)
        transformable_content = TransformableData(
            content=content_bytes, origin_format=entry.content_format
        )

        transform_strategy_class = selector.get_transform_strategy(
            self.input_args.transform_strategy_id,
        )
        transform_strategy = transform_strategy_class(
            target_format=self.input_args.target_format, data=transformable_content
        )
        transformer = Transformer(strategy=transform_strategy)
        data = transformer.transform()

        payload_address = self.payload_store.save(
            phase=Phase.TRANSFORM, payload=data.content
        )

        trns_entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.TRANSFORM,
            content_format=self.input_args.target_format,
            strategy_name=transform_strategy.__class__.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address),
        )
        return trns_entry_id

    def _decode(self, run_id: int) -> int:
        decode_strategy = selector.get_decode_strategy(self.input_args.source_as_path)
        decoder = Decoder(
            source_address=self.input_args.source_as_path, strategy=decode_strategy
        )
        data = decoder.decode()
        payload_address = self.payload_store.save(
            phase=Phase.DECODE, payload=data.content
        )

        entry_id = self.registry_store.save_entry(
            run_id=run_id,
            phase=Phase.DECODE,
            content_format=data.source_format,
            strategy_name=decode_strategy.__name__,
            content_hash=helpers.generate_hash(content=data.content),
            address=str(payload_address),
        )
        return entry_id

    def _fetch(self, run_id: int) -> int:
        fetch_strategy = selector.get_fetch_strategy(self.input_args.source_type)
        fetcher = Fetcher(
            source_address=self.input_args.source_address,
            strategy=fetch_strategy,
            table_name=self.input_args.source_table,
        )
        data = fetcher.fetch()
        payload_address = self.payload_store.save(
            phase=Phase.FETCH, payload=data.content
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
