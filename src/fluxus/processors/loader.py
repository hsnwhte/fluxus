from fluxus.strategies.protocols import LoadStrategyProtocol
from fluxus.models.dto import TransformedData
from fluxus.enums import ContentFormat


class Loader:
    def __init__(self, *, address: str, strategy: LoadStrategyProtocol, target_format: ContentFormat, table_name: str | None = None):
        self.address = address
        self.strategy = strategy
        self.target_format = target_format
        self.table_name = table_name

    def load(self, *, data: TransformedData) -> None:
        self.strategy.load(
            data=data,
            address=self.address,
            target_format=self.target_format,
            table_name=self.table_name,
        )