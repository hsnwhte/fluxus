import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData
from pluggle.strategies.decode.csv_decode_strategy import CsvDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.csv"
    )


@pytest.fixture
def source_file_path_malformed():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_malformed.csv"
    )


def test_decode_success(source_file_path_success: Path):
    data = CsvDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.CSV


def test_decode_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        CsvDecodeStrategy.decode(file_path=Path("nonexistent_file.csv"))


def test_decode_malformed(source_file_path_success: Path):
    with patch(
        "pluggle.strategies.decode.csv_decode_strategy.csv.Sniffer.sniff",
        side_effect=csv.Error("mocked sniff failure"),
    ):
        with pytest.raises(errors.DecodeMalformedError):
            CsvDecodeStrategy.decode(file_path=source_file_path_success)


def test_decode_permission_denied():
    with patch.object(Path, "read_bytes", side_effect=PermissionError):
        with pytest.raises(errors.DecodePermissionError):
            CsvDecodeStrategy.decode(file_path=Path("fake_path.csv"))
