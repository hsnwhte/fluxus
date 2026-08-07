from pluggle.models.dto import TransformableData
from pluggle.strategies.protocols import ExtractStrategyProtocol


class Extractor:
    def __init__(self, content: bytes, strategy: ExtractStrategyProtocol):
        self.content = content
        self.strategy = strategy

    def extract(self) -> TransformableData:
        return self.strategy.extract(content=self.content)
