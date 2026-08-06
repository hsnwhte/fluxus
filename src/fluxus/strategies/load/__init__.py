from fluxus.strategies.load.api_load_strategy import ApiLoadStrategy
from fluxus.strategies.load.db_load_strategy import DBLoadStrategy

LOAD_STRATEGY_MAP = {
    "db": DBLoadStrategy,
    "api": ApiLoadStrategy,
}
