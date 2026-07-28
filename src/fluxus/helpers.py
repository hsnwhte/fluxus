import hashlib

from fluxus.models.dto import ExtractableData
from fluxus.enums import ContentFormat


def to_extractable(*, content: str | bytes, format: ContentFormat)->ExtractableData:
    if isinstance(content, str):
        content = content.encode()
    return ExtractableData(content=content, source_format=format)

def generate_hash(content:bytes) ->str:
    return hashlib.sha256(content).hexdigest()