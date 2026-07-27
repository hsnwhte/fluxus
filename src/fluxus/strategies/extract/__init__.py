from .csv_extract_strategy import CsvExtractStrategy
from .html_extract_strategy import HtmlExtractStrategy
from .json_extract_strategy import JsonExtractStrategy
from .xml_extract_strategy import XmlExtractStrategy

EXTRACT_STRATEGY_MAP = {
    "csv": CsvExtractStrategy,
    "html": HtmlExtractStrategy,
    "json": JsonExtractStrategy,
    "xml": XmlExtractStrategy
}