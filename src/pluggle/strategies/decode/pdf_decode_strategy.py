from pathlib import Path

import pypdf
import pypdf.errors

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData


class PdfDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            _ = pypdf.PdfReader(file_path)
        except FileNotFoundError as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        except pypdf.errors.EmptyFileError as e:
            raise errors.DecodeEmptyFileError(f"Empty PDF file at {file_path}") from e
        except pypdf.errors.FileNotDecryptedError as e:
            raise errors.DecodePermissionError(
                f"Permission denied reading {file_path}"
            ) from e
        except pypdf.errors.PdfReadError as e:
            raise errors.DecodeMalformedError(f"Malformed PDF at {file_path}") from e
        content = file_path.read_bytes()
        return ExtractableData(content=content, source_format=ContentFormat.PDF)
