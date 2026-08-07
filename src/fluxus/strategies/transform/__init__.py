from pathlib import Path

from fluxus.strategies.protocols import TransformStrategyProtocol
from fluxus.strategies.transform.default import TransformStrategySamplePassthrough
from fluxus.strategies.transform.transform_installer import _load_strategy_from_file

TRANSFORM_STRATEGY_MAP: dict[str, type[TransformStrategyProtocol]] = {
    "default": TransformStrategySamplePassthrough,  # constant, not to be erased
}

_installed_dir = Path(__file__).resolve().parent / "installed"
_installed_dir.mkdir(exist_ok=True)

for file_path in sorted(_installed_dir.glob("*.py")):
    TRANSFORM_STRATEGY_MAP[file_path.stem] = _load_strategy_from_file(
        file_path=file_path
    )
