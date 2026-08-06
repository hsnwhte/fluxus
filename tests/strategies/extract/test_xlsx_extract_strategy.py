from pathlib import Path
from unittest.mock import patch
from xml.parsers.expat import ExpatError

import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import TransformableData
from fluxus.strategies.extract.xlsx_extract_strategy import XlsxExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.xlsx"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = XlsxExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.XLSX


def test_extract_bad_zip():
    invalid_zip_content = b"this is not a zip file"
    with pytest.raises(errors.ExtractSyntaxError):
        XlsxExtractStrategy.extract(content=invalid_zip_content)


def test_extract_expat_error(test_content: bytes):
    with patch(
        "fluxus.strategies.extract.xlsx_extract_strategy.xmltodict.parse",
        side_effect=ExpatError(),
    ):
        with pytest.raises(errors.ExtractSyntaxError):
            XlsxExtractStrategy.extract(content=test_content)
