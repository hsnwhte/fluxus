from pathlib import Path



### --- System adresses
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DB_PATH = PROJECT_ROOT / "data" / "pipeline.sqlite"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PIPELINE_STORE_ADDRESS = f"sqlite:///{_DB_PATH}"