from typing import Protocol
from fluxus.models.dto import ExtractableData

class FetchStrategyProtocol(Protocol):
    @staticmethod
    def fetch(*, address:str, table_name:str | None = None)-> ExtractableData:
        ...

class DecodeStrategyProtocol(Protocol):
    pass

class ExtractStrategyProtocol(Protocol):
    pass

class TransformStrategyProtocol(Protocol):
    pass

