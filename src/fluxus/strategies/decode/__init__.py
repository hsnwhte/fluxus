from .csv_decode_strategy import CsvDecodeStrategy
from .html_decode_strategy import HtmlDecodeStrategy
from .json_decode_strategy import JsonDecodeStrategy
from .xml_decode_stratgy import XmlDecodeStrategy

DECODE_STRATEGY_MAP = {
    "csv": CsvDecodeStrategy,
    "html": HtmlDecodeStrategy,
    "json": JsonDecodeStrategy,
    "xml": XmlDecodeStrategy
}