import enum


class Phase(enum.Enum):
    FETCH = "fetch"
    DECODE = "decode"
    EXTRACT = "extract"
    TRANSFORM = "transform"
    EXPORT = "export"
    LOAD = "load"


class ContentFormat(enum.Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"
    PDF = "pdf"


class MimeType(enum.Enum):
    JSON = "application/json"
    XML = "application/xml"
    CSV = "text/csv"
    HTML = "text/html"
    PNG = "image/png"
    JPEG = "image/jpeg"
    PDF = "application/pdf"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class FluxusIOType(enum.Enum):
    API = "api"
    DB = "db"
    FILE = "file"
