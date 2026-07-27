from pathlib import Path
from fluxus.strategies.protocols import FetchStrategyProtocol
from fluxus.models.dto import ExtractableData
from fluxus.enums import ExtractableFormat

class Fetcher:
    def __init__(self, *, source_address: str, strategy:FetchStrategyProtocol, table_name: str|None=None):
        self.address = source_address
        self.table_name = table_name
        self.strategy = strategy

    def fetch(self) ->ExtractableData:
        return self.strategy.fetch(address=self.address, table_name=self.table_name)

