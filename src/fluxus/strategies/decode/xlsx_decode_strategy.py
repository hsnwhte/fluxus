import zipfile
from pathlib import Path
from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import ExtractableData


class XlsxDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            content = file_path.read_bytes()
            if not zipfile.is_zipfile(file_path):
                raise errors.DecodeMalformedError(f"Not a valid XLSX file: {file_path}")
        except PermissionError as e:
            raise errors.DecodePermissionError(f"Permission denied reading {file_path}")
        return ExtractableData(content=content, source_format=ContentFormat.XLSX)
