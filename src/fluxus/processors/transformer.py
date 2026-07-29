from fluxus.strategies.protocols import TransformStrategyProtocol
from fluxus.models.dto import TransformedData

class Transformer:
    def __init__(self, *, strategy: TransformStrategyProtocol):
        self.strategy = strategy

    def transform(self) -> TransformedData:
        return self.strategy.transform()