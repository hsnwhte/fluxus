from pathlib import Path

from lxml import etree

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData


class XmlDecodeStrategy:
    @staticmethod
    def decode(*, file_path: Path) -> ExtractableData:
        try:
            tree = etree.parse(str(file_path))
        except (FileNotFoundError, OSError) as e:
            raise errors.DecodeSourceFileNotFoundError(
                f"Could not find or read file at {file_path}"
            ) from e
        except etree.XMLSyntaxError as e:
            raise errors.DecodeMalformedError(f"Malformed XML at {file_path}") from e
        content = etree.tostring(tree)
        return ExtractableData(content=content, source_format=ContentFormat.XML)
