from pathlib import Path
from fluxus.strategies import fetch, decode, extract, transform, load, export
from fluxus.strategies.protocols import FetchStrategyProtocol, DecodeStrategyProtocol, ExtractStrategyProtocol, TransformStrategyProtocol, LoadStrategyProtocol, ExportStrategyProtocol
from fluxus.exceptions import errors
from fluxus.enums import FluxusIOType, ContentFormat



class Selector:
    @staticmethod
    def get_fetch_strategy(source_type:FluxusIOType) -> FetchStrategyProtocol:
        smap = fetch.FETCH_STRATEGY_MAP
        try:
            return smap[source_type.value]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                f"No fetch strategy for '{source_type.value}' could be found."
            ) from e

    @staticmethod
    def get_decode_strategy(source_address: Path) -> DecodeStrategyProtocol:
        file_ext = source_address.suffix.lstrip(".")
        smap = decode.DECODE_STRATEGY_MAP
        try:
            return smap[file_ext]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                f"No decode strategy for '{file_ext}' could be found."
            ) from e

    @staticmethod
    def get_extract_strategy(source_format:ContentFormat) -> ExtractStrategyProtocol:
        smap = extract.EXTRACT_STRATEGY_MAP
        try:
            return smap[source_format.value]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                f"No extract strategy for '{source_format.value}' could be found."
            ) from e

    @staticmethod
    def get_transform_strategy(strategy_name:str)->TransformStrategyProtocol:
        smap = transform.TRANSFORM_STRATEGY_MAP
        try:
            return smap[strategy_name]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                f"No transform strategy for '{strategy_name}' could be found."
            ) from e

    @staticmethod
    def get_load_strategy(target_type: FluxusIOType) -> LoadStrategyProtocol:
        smap = load.LOAD_STRATEGY_MAP
        try:
            return smap[target_type.value]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                f"No load strategy for '{target_type.value}' could be found."
            ) from e

    @staticmethod
    def get_export_strategy() -> ExportStrategyProtocol:
        smap = export.EXPORT_STRATEGY_MAP
        try:
            return smap["file"]
        except KeyError as e:
            raise errors.StrategyNotFoundError(
                "No export strategy could be found."
            ) from e




selector = Selector()

