import pytest
from pathlib import Path

from fluxus.exceptions import errors
from fluxus.enums import ContentFormat
from fluxus.models.dto import ExtractableData
from fluxus.strategies.decode.xml_decode_stratgy import XmlDecodeStrategy

@pytest.fixture
def source_file_path_success():
    return Path(__file__).resolve().parent / "test_sample_success.xml"

@pytest.fixture
def source_file_path_malformed():
    return Path(__file__).resolve().parent / "test_sample_malformed.xml"


def test_decode_success(source_file_path_success:Path):
    data = XmlDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.XML


def test_decode_malformed(source_file_path_malformed:Path):
    with pytest.raises(errors.DecodeMalformedError):
        XmlDecodeStrategy.decode(file_path=source_file_path_malformed)
