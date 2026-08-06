import hashlib
from uuid import uuid4

from fluxus.enums import ContentFormat, MimeType
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData


def generate_strategy_uid() -> str:
    return uuid4().hex[:12]


def to_extractable(
    *, content: str | bytes, content_format: ContentFormat
) -> ExtractableData:
    if isinstance(content, str):
        content = content.encode()
    return ExtractableData(content=content, source_format=content_format)


def generate_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def content_format_to_mime(content_format: ContentFormat) -> MimeType:
    try:
        return MimeType[content_format.name]
    except KeyError as e:
        raise errors.SerializationError(
            f"No MimeType mapping for ContentFormat '{content_format.name}'"
        ) from e


def mime_to_content_format(mime_type: MimeType) -> ContentFormat:
    try:
        return ContentFormat[mime_type.name]
    except KeyError as e:
        raise errors.SerializationError(
            f"No ContentFormat mapping for MimeType '{mime_type.name}'"
        ) from e
