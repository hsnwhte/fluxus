import pytest
from pathlib import Path
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData
from fluxus.strategies.extract.xml_extract_strategy import XmlExtractStrategy

@pytest.fixture
def test_content():
    path = Path(__file__).resolve().parent / "test_sample_success.xml"
    return path.read_bytes()

def test_extract_success(test_content:bytes):
    data = XmlExtractStrategy.extract(content=test_content)

    assert isinstance(data, TransformableData)
    assert isinstance(data.content, bytes)
    assert data.content is not None
    assert data.origin_format == ContentFormat.XML


