from fluxus.strategies.load.db_load_strategy import DBLoadStrategy
from fluxus.strategies.load.api_load_strategy import ApiLoadStrategy

LOAD_STRATEGY_MAP = {
    "db": DBLoadStrategy,
    "api": ApiLoadStrategy,
}