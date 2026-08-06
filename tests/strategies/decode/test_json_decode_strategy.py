from pathlib import Path
from unittest.mock import patch

import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import ExtractableData
from fluxus.strategies.decode.json_decode_strategy import JsonDecodeStrategy


@pytest.fixture
def source_file_path_success():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.json"
    )


@pytest.fixture
def source_file_path_malformed():
    return (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_malformed.json"
    )


def test_decode_success(source_file_path_success: Path):
    data = JsonDecodeStrategy.decode(file_path=source_file_path_success)

    assert isinstance(data, ExtractableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.source_format == ContentFormat.JSON


def test_decode_malformed(source_file_path_malformed: Path):
    with pytest.raises(errors.DecodeMalformedError):
        JsonDecodeStrategy.decode(file_path=source_file_path_malformed)


def test_decode_source_file_not_found():
    with pytest.raises(errors.DecodeSourceFileNotFoundError):
        JsonDecodeStrategy.decode(file_path=Path("nonexistent_file.json"))


def test_decode_permission_denied():
    with patch.object(Path, "read_bytes", side_effect=PermissionError):
        with pytest.raises(errors.DecodePermissionError):
            JsonDecodeStrategy.decode(file_path=Path("fake_path.json"))
