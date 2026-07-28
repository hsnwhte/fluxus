from pathlib import Path
from fluxus.models.dto import TransformedData

class ExportStrategy:
    @staticmethod
    def export(*, data:TransformedData, file_path: Path) -> None:
        file_path.write_bytes(data.content)



