from fluxus.strategies.protocols import ExtractStrategyProtocol
from fluxus.models.dto import TransformableData

class Extractor:
    def __init__(self, content:bytes, strategy:ExtractStrategyProtocol):
        self.content = content
        self.strategy=strategy

    def extract(self) ->TransformableData:
        return self.strategy.extract(content=self.content)