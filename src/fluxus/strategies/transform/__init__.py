from pathlib import Path
from fluxus.strategies.transform.transform_installer import _load_strategy_from_file
from fluxus.strategies.transform.transform_strategy_sample_passthrough import (
    TransformStrategySamplePassthrough,
)

TRANSFORM_STRATEGY_MAP: dict[int, type] = {
    0: TransformStrategySamplePassthrough,  # constant, not to be erased
}

_installed_dir = Path(__file__).resolve().parent / "installed"
_installed_dir.mkdir(exist_ok=True)

for i, file_path in enumerate(sorted(_installed_dir.glob("*.py")), start=1):
    TRANSFORM_STRATEGY_MAP[i] = _load_strategy_from_file(file_path=file_path)
