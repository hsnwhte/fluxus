import csv
import json
import io

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData


class CsvExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            decoded = content.decode(encoding="utf-8")
            parsed = csv.DictReader(io.StringIO(decoded))
            rows = list(parsed)
        except (UnicodeDecodeError, csv.Error) as e:
            raise errors.ExtractSyntaxError(f"Malformed CSV content: {e}") from e
        content = json.dumps(rows).encode()
        return TransformableData(content=content, origin_format=ContentFormat.CSV)
