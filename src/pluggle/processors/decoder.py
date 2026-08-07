from pathlib import Path

from pluggle.models.dto import ExtractableData
from pluggle.strategies.protocols import DecodeStrategyProtocol


class Decoder:
    def __init__(self, *, source_address: Path, strategy: DecodeStrategyProtocol):
        self.address = source_address
        self.strategy = strategy

    def decode(self) -> ExtractableData:
        return self.strategy.decode(file_path=self.address)
