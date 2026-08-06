from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData
from fluxus.strategies.decode.html_decode_strategy import HtmlDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.html"
    )


@pytest.fixture
def source_file_path_malformed():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_malformed.html"
    )


def test_decode_success(source_file_path_success: Path):
    data = HtmlDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.HTML


def test_decode_malformed(source_file_path_success: Path):
    with patch(
        "fluxus.strategies.decode.html_decode_strategy.html.parse",
        side_effect=etree.ParseError("mocked_error", 0, 0, 0),
    ):
        with pytest.raises(errors.DecodeMalformedError):
            HtmlDecodeStrategy.decode(file_path=source_file_path_success)


def test_decode_source_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        HtmlDecodeStrategy.decode(file_path=Path("nonexistent_file.html"))
