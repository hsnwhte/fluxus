from pathlib import Path

DEV_ROOT_DIR = Path(__file__).resolve().parent

DEV_PIPELINE_DB_URL = f"sqlite:///{DEV_ROOT_DIR / 'databases' / 'dev_pipeline.sqlite'}"

DEV_SOURCE_API_URL = "https://jsonplaceholder.typicode.com/todos/1"
DEV_SOURCE_DB_URL = f"sqlite:///{DEV_ROOT_DIR / 'databases' / 'dev_source.sqlite'}"
DEV_SOURCE_FILE_DIR = DEV_ROOT_DIR / "test_data" / "input"
DEV_TARGET_API_URL = "https://jsonplaceholder.typicode.com/posts/1"
DEV_TARGET_DB_URL = f"sqlite:///{DEV_ROOT_DIR / 'databases' / 'dev_target.sqlite'}"
DEV_TARGET_FILE_DIR = DEV_ROOT_DIR / "test_data" / "output"
