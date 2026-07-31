import xmltodict
import json
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData


class XmlExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        parsed = xmltodict.parse(content.decode())
        content_bytes = json.dumps(parsed).encode()
        result = TransformableData(
            content=content_bytes, origin_format=ContentFormat.XML
        )
        return result
