import json
from pathlib import Path

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData


class JsonDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            content = file_path.read_bytes()
            json.loads(content)
        except FileNotFoundError as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        except PermissionError as e:
            raise errors.DecodePermissionError(
                f"Permission denied reading {file_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise errors.DecodeMalformedError(f"Malformed JSON at {file_path}") from e
        return ExtractableData(content=content, source_format=ContentFormat.JSON)
