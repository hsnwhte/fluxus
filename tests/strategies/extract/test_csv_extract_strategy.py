import pytest
import json
from pathlib import Path
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData
from fluxus.strategies.extract.csv_extract_strategy import CsvExtractStrategy
from fluxus.exceptions import errors


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.csv"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = CsvExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.CSV


def test_extract_unicode_decode_error():
    invalid_utf8_content = b"\xff\xfe invalid utf-8 bytes"
    with pytest.raises(errors.ExtractMalformedError):
        CsvExtractStrategy.extract(content=invalid_utf8_content)
