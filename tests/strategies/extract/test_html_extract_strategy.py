from pathlib import Path

import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData
from pluggle.strategies.extract.html_extract_strategy import HtmlExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.html"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = HtmlExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.HTML


def test_extract_malformed():
    malformed_content = b""
    with pytest.raises(errors.ExtractSyntaxError):
        HtmlExtractStrategy.extract(content=malformed_content)
