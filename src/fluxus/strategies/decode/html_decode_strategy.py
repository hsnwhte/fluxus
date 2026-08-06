from pathlib import Path

from lxml import etree, html

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData


class HtmlDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            tree = html.parse(str(file_path))
        except etree.ParseError as e:
            raise errors.DecodeMalformedError(f"Malformed HTML at {file_path}") from e
        except (OSError, FileNotFoundError) as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        content = etree.tostring(tree)
        return ExtractableData(content=content, source_format=ContentFormat.HTML)
