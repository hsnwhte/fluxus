import csv
import json
import io
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData


class CsvExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        decoded = content.decode(encoding="utf-8")
        parsed = csv.DictReader(io.StringIO(decoded))
        rows = list(parsed)
        content = json.dumps(rows).encode()
        return TransformableData(content=content, origin_format=ContentFormat.CSV)
