from .csv_extract_strategy import CsvExtractStrategy
from .html_extract_strategy import HtmlExtractStrategy
from .json_extract_strategy import JsonExtractStrategy
from .xml_extract_strategy import XmlExtractStrategy
from .docx_extract_strategy import DocxExtractStrategy
from .xlsx_extract_strategy import XlsxExtractStrategy
from .pdf_extract_strategy import PdfExtractStrategy

EXTRACT_STRATEGY_MAP = {
    "csv": CsvExtractStrategy,
    "docx": DocxExtractStrategy,
    "html": HtmlExtractStrategy,
    "json": JsonExtractStrategy,
    "pdf": PdfExtractStrategy,
    "xlsx": XlsxExtractStrategy,
    "xml": XmlExtractStrategy,
}
