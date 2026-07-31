from .csv_decode_strategy import CsvDecodeStrategy
from .docx_decode_strategy import DocxDecodeStrategy
from .html_decode_strategy import HtmlDecodeStrategy
from .json_decode_strategy import JsonDecodeStrategy
from .pdf_decode_strategy import PdfDecodeStrategy
from .xlsx_decode_strategy import XlsxDecodeStrategy
from .xml_decode_stratgy import XmlDecodeStrategy

DECODE_STRATEGY_MAP = {
    "csv": CsvDecodeStrategy,
    "docx": DocxDecodeStrategy,
    "html": HtmlDecodeStrategy,
    "json": JsonDecodeStrategy,
    "pdf": PdfDecodeStrategy,
    "xlsx": XlsxDecodeStrategy,
    "xml": XmlDecodeStrategy,
}
