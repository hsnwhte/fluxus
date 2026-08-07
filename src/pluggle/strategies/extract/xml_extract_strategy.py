import json
from pyexpat import ExpatError

import xmltodict

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData


class XmlExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            parsed = xmltodict.parse(content.decode())
        except (UnicodeDecodeError, ExpatError) as e:
            raise errors.ExtractSyntaxError(f"Malformed XML content: {e}") from e
        content_bytes = json.dumps(parsed).encode()
        result = TransformableData(
            content=content_bytes, origin_format=ContentFormat.XML
        )
        return result
