from pathlib import Path
from unittest.mock import patch

import pypdf
import pytest

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import ExtractableData
from pluggle.strategies.decode.pdf_decode_strategy import PdfDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.pdf"
    )


def test_decode_success(source_file_path_success: Path):
    data = PdfDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.PDF


def test_decode_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        PdfDecodeStrategy.decode(file_path=Path("nonexistent_file.pdf"))


def test_decode_empty_file(tmp_path: Path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    with pytest.raises(errors.DecodeEmptyFileError):
        PdfDecodeStrategy.decode(file_path=empty_file)


def test_decode_not_decrypted():
    # noinspection PyUnresolvedReferences
    with patch(
        "pluggle.strategies.decode.pdf_decode_strategy.pypdf.PdfReader",
        side_effect=pypdf.errors.FileNotDecryptedError,
    ):
        with pytest.raises(errors.DecodePermissionError):
            PdfDecodeStrategy.decode(file_path=Path("fake_path.pdf"))


def test_decode_malformed():
    # noinspection PyUnresolvedReferences
    with patch(
        "pluggle.strategies.decode.pdf_decode_strategy.pypdf.PdfReader",
        side_effect=pypdf.errors.PdfReadError,
    ):
        with pytest.raises(errors.DecodeMalformedError):
            PdfDecodeStrategy.decode(file_path=Path("fake_path.pdf"))
