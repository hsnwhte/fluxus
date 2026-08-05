import pytest
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData, TransformedData
from fluxus.strategies.transform.default import (
    TransformStrategySamplePassthrough,
)


@pytest.fixture
def sample_transformable_data():
    return TransformableData(
        content=b'{"key": "value"}', origin_format=ContentFormat.JSON
    )


def test_passthrough_transform_returns_unchanged_content(
    sample_transformable_data: TransformableData,
):
    strategy = TransformStrategySamplePassthrough(
        target_format=ContentFormat.JSON,
        data=sample_transformable_data,
    )

    result = strategy.transform()

    assert isinstance(result, TransformedData)
    assert result.content == sample_transformable_data.content
