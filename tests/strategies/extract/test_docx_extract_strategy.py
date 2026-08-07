from pathlib import Path
from unittest.mock import patch

import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData
from pluggle.strategies.extract.docx_extract_strategy import DocxExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.docx"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = DocxExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.DOCX


def test_extract_bad_zip():
    invalid_zip_content = b"this is not a zip file"
    with pytest.raises(errors.ExtractSyntaxError):
        DocxExtractStrategy.extract(content=invalid_zip_content)


def test_extract_expat_error(test_content: bytes):
    with (
        patch(
            "pluggle.strategies.extract.docx_extract_strategy.xmltodict.parse",
            side_effect=__import__(
                "xml.parsers.expat", fromlist=["ExpatError"]
            ).ExpatError(),
        ),
        pytest.raises(errors.ExtractSyntaxError),
    ):
        DocxExtractStrategy.extract(content=test_content)
