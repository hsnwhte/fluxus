from pathlib import Path
from unittest.mock import patch

import pypdf
import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData
from pluggle.strategies.extract.pdf_extract_strategy import PdfExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.pdf"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = PdfExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.PDF


def test_extract_malformed():
    # noinspection PyUnresolvedReferences
    with patch(
        "pluggle.strategies.extract.pdf_extract_strategy.pypdf.PdfReader",
        side_effect=pypdf.errors.PdfReadError,
    ):
        with pytest.raises(errors.ExtractSyntaxError):
            PdfExtractStrategy.extract(content=b"not a real pdf")
