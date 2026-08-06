from pathlib import Path

from fluxus.models.dto import TransformedData
from fluxus.strategies.protocols import ExportStrategyProtocol


class Exporter:
    def __init__(self, *, file_path: Path, strategy: ExportStrategyProtocol):
        self.file_path = file_path
        self.strategy = strategy

    def export(self, *, data: TransformedData) -> None:
        self.strategy.export(
            data=data,
            file_path=self.file_path,
        )
