from typing import Protocol
from pathlib import Path
from fluxus.models.dto import ExtractableData

class FetchStrategyProtocol(Protocol):
    @staticmethod
    def fetch(*, address:str, table_name:str | None = None)-> ExtractableData:
        ...

class DecodeStrategyProtocol(Protocol):
    @staticmethod
    def decode(*, file_path:Path) ->ExtractableData:
        ...

class ExtractStrategyProtocol(Protocol):
    pass

class TransformStrategyProtocol(Protocol):
    pass

