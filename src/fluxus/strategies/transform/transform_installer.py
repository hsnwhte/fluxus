from pathlib import Path
import importlib.util
import shutil
from fluxus.exceptions import errors
from fluxus.strategies.protocols import TransformStrategyProtocol


def install_strategy(*, strategy_path: Path) -> int:
    _load_strategy_from_file(file_path=strategy_path)

    installed_dir = Path(__file__).resolve().parent / "installed"
    installed_dir.mkdir(exist_ok=True)

    existing_files = sorted(installed_dir.glob("*.py"))
    next_id = len(existing_files) + 1
    destination = installed_dir / f"strategy_{next_id}.py"

    shutil.copy(strategy_path, destination)

    return next_id


def uninstall_strategy(*, strategy_id: int) -> None:
    if strategy_id == 0:
        raise errors.StrategyNotFoundError(
            "Cannot uninstall the default strategy (id 0)."
        )
    installed_dir = Path(__file__).resolve().parent / "installed"
    files = sorted(installed_dir.glob("*.py"))

    index = strategy_id - 1
    if index < 0 or index >= len(files):
        raise errors.StrategyNotFoundError(
            f"No installed strategy with id {strategy_id}."
        )

    files[index].unlink()


def _load_strategy_from_file(*, file_path: Path) -> type:
    try:
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
        else:
            raise errors.StrategyNotFoundError(
                f"Module spec could not be created for {file_path}."
            )
        if spec.loader:
            spec.loader.exec_module(module)
        else:
            raise errors.StrategyNotFoundError(
                f"Module loader could not be created for {file_path}."
            )
    except (SyntaxError, FileNotFoundError) as e:
        raise errors.StrategyNotFoundError(
            f"Failed to load strategy {file_path}: {e}"
        ) from e

    matches = [name for name in dir(module) if name.startswith("TransformStrategy")]
    if len(matches) == 0:
        raise errors.StrategyNotFoundError(
            f"No class starting with 'TransformStrategy' found in {file_path}"
        )
    if len(matches) > 1:
        raise errors.StrategyNotFoundError(
            f"Multiple classes starting with 'TransformStrategy' found in {file_path}: {matches}. Exactly one is required."
        )
    strategy_class = getattr(module, matches[0])
    if not issubclass(strategy_class, TransformStrategyProtocol):
        raise errors.StrategyNotFoundError(
            f"{strategy_class.__class__.__name__} does not implement TransformStrategyProtocol"
        )
    return strategy_class
