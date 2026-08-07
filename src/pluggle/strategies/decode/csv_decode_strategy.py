import csv
from pathlib import Path

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData


class CsvDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            content = file_path.read_bytes()
            with open(file_path, newline="", encoding="utf-8") as f:
                csv.Sniffer().sniff(f.read(2048))
        except FileNotFoundError as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        except PermissionError as e:
            raise errors.DecodePermissionError(
                f"Permission denied reading {file_path}"
            ) from e
        except csv.Error as e:
            raise errors.DecodeMalformedError(f"Malformed CSV at {file_path}") from e

        return ExtractableData(content=content, source_format=ContentFormat.CSV)
