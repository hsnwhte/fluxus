from .api_fetch_strategy import ApiFetchStrategy
from .db_fetch_strategy import DBFetchStrategy

FETCH_STRATEGY_MAP = {
    "api": ApiFetchStrategy,
    "db": DBFetchStrategy
}

