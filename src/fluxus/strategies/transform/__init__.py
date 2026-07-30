from fluxus.strategies.transform.transform_strategy_for_sample_comments_json import (
    TransformStrategyForSampleCommentsJson,
)
from fluxus.strategies.transform.sample_passthrough_transform_strategy import (
    SamplePassthroughTransformStrategy,
)

TRANSFORM_STRATEGY_MAP = {
    "sample_passthrough": SamplePassthroughTransformStrategy,
    "sample_comments": TransformStrategyForSampleCommentsJson,
}
