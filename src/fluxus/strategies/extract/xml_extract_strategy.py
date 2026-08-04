import xmltodict
import json

from pyexpat import ExpatError

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData


class XmlExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            parsed = xmltodict.parse(content.decode())
        except (UnicodeDecodeError, ExpatError) as e:
            raise errors.ExtractMalformedError(f"Malformed XML content: {e}") from e
        content_bytes = json.dumps(parsed).encode()
        result = TransformableData(
            content=content_bytes, origin_format=ContentFormat.XML
        )
        return result
