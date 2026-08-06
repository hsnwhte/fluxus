from fluxus.models.dto import TransformedData
from fluxus.strategies.protocols import TransformStrategyProtocol


class Transformer:
    def __init__(self, *, strategy: TransformStrategyProtocol):
        self.strategy = strategy

    def transform(self) -> TransformedData:
        return self.strategy.transform()
