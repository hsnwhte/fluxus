import json
from fluxus.models.dto import TransformableData
from fluxus.enums import ContentFormat
from fluxus.exceptions import errors


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
