import zipfile
from pathlib import Path

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData


class XlsxDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            content = file_path.read_bytes()
            if not zipfile.is_zipfile(file_path):
                raise errors.DecodeMalformedError(f"Not a valid XLSX file: {file_path}")
        except FileNotFoundError as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        except PermissionError as e:
            raise errors.DecodePermissionError(
                f"Permission denied reading {file_path}"
            ) from e
        return ExtractableData(content=content, source_format=ContentFormat.XLSX)
