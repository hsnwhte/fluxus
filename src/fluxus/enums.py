import enum

class Phase(enum.Enum):
    FETCH = "fetch"
    DECODE = "decode"
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"

class ContentFormat(enum.Enum):
    CSV="csv"
    JSON="json"
    XML="xml"
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