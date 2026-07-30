import json
from fluxus.models.dto import TransformableData
from fluxus.enums import ContentFormat
from fluxus.exceptions import errors


class JsonExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            parsed = json.loads(content)
            # EDGE CASE: some sources (e.g. API endpoints returning a single
            # resource, like /todos/1) return a bare JSON object instead of a
            # list. Internal canonical format is always list[dict], so a single
            # object is wrapped into a one-element list here.
            if isinstance(parsed, dict):
                parsed = [parsed]

        except json.JSONDecodeError as e:
            raise errors.ExtractMalformedError(f"Malformed JSON: {e}") from e

        normalized = json.dumps(parsed, ensure_ascii=False).encode()

        return TransformableData(content=normalized, origin_format=ContentFormat.JSON)
