from pluggle.strategies.load.api_load_strategy import ApiLoadStrategy
from pluggle.strategies.load.db_load_strategy import DBLoadStrategy

LOAD_STRATEGY_MAP = {
    "db": DBLoadStrategy,
    "api": ApiLoadStrategy,
}
