from typing import Protocol
from pathlib import Path
from fluxus.models.dto import ExtractableData, TransformableData, TransformedData
from fluxus.enums import ContentFormat

class FetchStrategyProtocol(Protocol):
    @staticmethod
    def fetch(*, address:str, table_name:str | None = None)-> ExtractableData:
        ...

class DecodeStrategyProtocol(Protocol):
    @staticmethod
    def decode(*, file_path:Path) ->ExtractableData:
        ...

class ExtractStrategyProtocol(Protocol):
    @staticmethod
    def extract(*, content: bytes) ->TransformableData:
        ...

class TransformStrategyProtocol(Protocol):
    def __init__(self, *, target_format:ContentFormat, data:TransformableData, **kwargs):
        ...
    def transform(self) ->TransformedData:
        ...

class LoadStrategyProtocol(Protocol):
    @staticmethod
    def load(*, data:TransformedData, address:str, target_format:ContentFormat, table_name:str | None = None)-> None:
        ...

class ExportStrategyProtocol(Protocol):
    @staticmethod
    def export(*, data:TransformedData, file_path:Path)-> None:
        ...
