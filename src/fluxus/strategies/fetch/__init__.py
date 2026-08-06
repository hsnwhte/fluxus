from fluxus.strategies.fetch.api_fetch_strategy import ApiFetchStrategy
from fluxus.strategies.fetch.db_fetch_strategy import DBFetchStrategy

FETCH_STRATEGY_MAP = {"api": ApiFetchStrategy, "db": DBFetchStrategy}
