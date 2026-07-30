from pathlib import Path
from fluxus.enums import ContentFormat

### --- SYSTEM ADDRESSES
# ----- Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# ----- Pipeline Store
_DB_PATH = PROJECT_ROOT / "data" / "runtime.sqlite"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
PIPELINE_STORE_ADDRESS = f"sqlite:///{_DB_PATH}"
# ----- Log Output
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


### --- System variables
NORMALIZED_FORMAT = ContentFormat.JSON
