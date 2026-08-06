from .csv_extract_strategy import CsvExtractStrategy
from .docx_extract_strategy import DocxExtractStrategy
from .html_extract_strategy import HtmlExtractStrategy
from .json_extract_strategy import JsonExtractStrategy
from .pdf_extract_strategy import PdfExtractStrategy
from .xlsx_extract_strategy import XlsxExtractStrategy
from .xml_extract_strategy import XmlExtractStrategy

EXTRACT_STRATEGY_MAP = {
    "csv": CsvExtractStrategy,
    "docx": DocxExtractStrategy,
    "html": HtmlExtractStrategy,
    "json": JsonExtractStrategy,
    "pdf": PdfExtractStrategy,
    "xlsx": XlsxExtractStrategy,
    "xml": XmlExtractStrategy,
}
