from .api_fetch_strategy import APIFetchStrategy
from .db_fetch_strategy import DBFetchStrategy

FETCH_STRATEGY_MAP = {
    "api": APIFetchStrategy,
    "db": DBFetchStrategy
}

