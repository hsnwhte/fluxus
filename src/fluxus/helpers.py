from fluxus.models.dto import ExtractableData
from fluxus.enums import ExtractableFormat


def to_extractable(*, content: str | bytes, format: ExtractableFormat)->ExtractableData:
    if isinstance(content, str):
        content = content.encode()
    return ExtractableData(content=content, format=format)