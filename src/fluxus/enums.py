import enum

class Phase(enum.Enum):
    FETCH = "fetch"
    DECODE = "decode"
    EXTRACT = "extract"
    TRANSFORM = "transform"
    EXPORT = "export"
    LOAD = "load"

class ContentFormat(enum.Enum):
    JSON="json"
    XML="xml"
    CSV="csv"
    HTML="html"

class MimeType(enum.Enum):
    JSON = "application/json"
    XML = "application/xml"
    CSV = "text/csv"
    HTML = "text/html"

class FluxusIOType(enum.Enum):
    API="api"
    DB= "db"
    FILE="file"