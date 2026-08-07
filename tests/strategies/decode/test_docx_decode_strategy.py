from pathlib import Path
from unittest.mock import patch

import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData
from fluxus.strategies.decode.docx_decode_strategy import DocxDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.docx"
    )


def test_decode_success(source_file_path_success: Path):
    data = DocxDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.DOCX


def test_decode_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        DocxDecodeStrategy.decode(file_path=Path("nonexistent_file.docx"))


def test_decode_malformed(source_file_path_success):
    with (
        patch(
            "fluxus.strategies.decode.docx_decode_strategy.zipfile.is_zipfile",
            return_value=False,
        ),
        pytest.raises(errors.DecodeMalformedError),
    ):
        DocxDecodeStrategy.decode(file_path=source_file_path_success)


def test_decode_permission_denied():
    with patch.object(Path, "read_bytes", side_effect=PermissionError):
        with pytest.raises(errors.DecodePermissionError):
            DocxDecodeStrategy.decode(file_path=Path("fake_path.docx"))
