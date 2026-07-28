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

class FluxusIOType(enum.Enum):
    API="api"
    DB= "db"
    FILE="file"