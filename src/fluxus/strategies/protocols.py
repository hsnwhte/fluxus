from typing import Protocol
from pathlib import Path
from fluxus.models.dto import ExtractableData, TransformableData

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
    pass

