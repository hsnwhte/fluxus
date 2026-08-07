import json

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData


class JsonExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                parsed = [parsed]
        except json.JSONDecodeError as e:
            raise errors.ExtractSyntaxError(f"Malformed JSON: {e}") from e

        normalized = json.dumps(parsed, ensure_ascii=False).encode()

        return TransformableData(content=normalized, origin_format=ContentFormat.JSON)
