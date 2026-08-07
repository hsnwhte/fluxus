import enum


class Phase(enum.Enum):
    FETCH = "fetch"
    DECODE = "decode"
    EXTRACT = "extract"
    TRANSFORM = "transform"
    EXPORT = "export"
    LOAD = "load"


class RunStatus(enum.Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    INTERRUPTED = "interrupted"


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


class CliListType(enum.Enum):
    RUNS = "runs"
    REGISTRY = "registry"
    STRATEGIES = "strategies"


class CliInspectType(enum.Enum):
    REGISTRY = "registry"
    PAYLOAD = "payload"
