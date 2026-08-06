from pathlib import Path

import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import TransformableData
from fluxus.strategies.extract.xml_extract_strategy import XmlExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.xml"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = XmlExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.XML


def test_extract_malformed():
    malformed_content = b"this is not valid xml <<<"
    with pytest.raises(errors.ExtractSyntaxError):
        XmlExtractStrategy.extract(content=malformed_content)


def test_extract_unicode_decode_error():
    invalid_utf8_content = b"\xff\xfe invalid utf-8 bytes"
    with pytest.raises(errors.ExtractSyntaxError):
        XmlExtractStrategy.extract(content=invalid_utf8_content)
