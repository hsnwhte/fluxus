import json
import xmltodict
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData


class HtmlExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        parsed = xmltodict.parse(content.decode(encoding="utf-8"))
        content_bytes = json.dumps(parsed).encode()
        result = TransformableData(
            content=content_bytes, origin_format=ContentFormat.HTML
        )
        return result
