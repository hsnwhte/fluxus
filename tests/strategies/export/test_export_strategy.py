from pathlib import Path
from fluxus.models.dto import TransformedData
from fluxus.strategies.export.export_strategy import ExportStrategy


def test_export_strategy_writes_content(tmp_path:Path):
    file_path = tmp_path / "output.json"
    data = TransformedData(content=b'{"key": "value"}')

    ExportStrategy.export(data=data, file_path=file_path)

    assert file_path.read_bytes() == b'{"key": "value"}'