from pathlib import Path
from unittest.mock import patch

import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData
from pluggle.strategies.decode.xlsx_decode_strategy import XlsxDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.xlsx"
    )


def test_decode_success(source_file_path_success: Path):
    data = XlsxDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.XLSX


def test_decode_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        XlsxDecodeStrategy.decode(file_path=Path("nonexistent_file.xlsx"))


def test_decode_malformed(source_file_path_success):
    with patch(
        "pluggle.strategies.decode.xlsx_decode_strategy.zipfile.is_zipfile",
        return_value=False,
    ):
        with pytest.raises(errors.DecodeMalformedError):
            XlsxDecodeStrategy.decode(file_path=source_file_path_success)


def test_decode_permission_denied():
    with patch.object(Path, "read_bytes", side_effect=PermissionError):
        with pytest.raises(errors.DecodePermissionError):
            XlsxDecodeStrategy.decode(file_path=Path("fake_path.xlsx"))
