from pathlib import Path

from fluxus.models.dto import ExtractableData
from fluxus.strategies.protocols import DecodeStrategyProtocol


class Decoder:
    def __init__(self, *, source_address: Path, strategy: DecodeStrategyProtocol):
        self.address = source_address
        self.strategy = strategy

    def decode(self) -> ExtractableData:
        return self.strategy.decode(file_path=self.address)
