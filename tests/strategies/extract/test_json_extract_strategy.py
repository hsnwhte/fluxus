import json
from pathlib import Path

import pytest

from fluxus.enums import ContentFormat
from fluxus.exceptions import errors
from fluxus.models.dto import TransformableData
from fluxus.strategies.extract.json_extract_strategy import JsonExtractStrategy


@pytest.fixture
def test_content():
    path = (
        Path(__file__).resolve().parent.parent
        / "sample_files"
        / "test_sample_success.json"
    )
    return path.read_bytes()


def test_extract_success(test_content: bytes):
    data = JsonExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.JSON


def test_extract_malformed():
    malformed_content = b'{"key": invalid}'
    with pytest.raises(errors.ExtractSyntaxError):
        JsonExtractStrategy.extract(content=malformed_content)


def test_extract_wraps_bare_object_in_list():
    bare_object_content = b'{"id": 1, "name": "test"}'
    data = JsonExtractStrategy.extract(content=bare_object_content)
    parsed = json.loads(data.content)

    assert isinstance(parsed, list)
    assert parsed == [{"id": 1, "name": "test"}]
