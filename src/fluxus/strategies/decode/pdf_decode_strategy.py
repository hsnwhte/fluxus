from pathlib import Path
import pypdf, pypdf.errors
from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import ExtractableData


class PdfDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            _ = pypdf.PdfReader(file_path)
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
