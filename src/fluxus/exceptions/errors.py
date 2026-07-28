from fluxus.enums import Phase

# --- Root ---
class FluxusError(Exception):
    """Common ancestor for all errors raised by Fluxus."""

# --- Orchestration axis ---
class OrchestrationError(FluxusError):
    """Errors related to orchestration of pipeline phases."""

class InvalidInputError(OrchestrationError):
    """Errors stemming from invalid arguments/inputs by UI."""

class StrategyNotFoundError(OrchestrationError):
    """Errors occuring when selector is selecting strategies."""

# --- Diachronic axis: organized by pipeline phase ---
class FetchError(FluxusError):
    """Errors occurring while fetching data from a source."""

class FetchApiError(FetchError):
    """Errors occuring when fetching from an API Endpoint"""

class FetchDbError(FetchError):
    """Errors occuring when fetching from a Database"""

class FetchBadRequestError(FetchApiError):
    """The request to the source was malformed (HTTP 400)."""
    def __init__(self, address: str):
        message = f"Bad request to source '{address}' (HTTP 400)."
        super().__init__(message)

class FetchNotAuthorizedError(FetchApiError):
    """Access to the specified source/address is unauthorized or forbidden (HTTP 401/403)."""
    def __init__(self, address: str, status_code: int):
        message = f"Not authorized to access source '{address}' (HTTP {status_code})."
        super().__init__(message)

class FetchNotFoundError(FetchApiError):
    """The specified source/address could not be found (HTTP 404)."""
    def __init__(self, address: str):
        message = f"Source '{address}' could not be found (HTTP 404)."
        super().__init__(message)

class FetchRateLimitError(FetchApiError):
    """The source rejected the request due to rate limiting (HTTP 429)."""
    def __init__(self, address: str):
        message = f"Rate limit exceeded when accessing source '{address}' (HTTP 429)."
        super().__init__(message)

class FetchServerError(FetchApiError):
    """The source's server encountered an error (HTTP 5xx)."""
    def __init__(self, address: str, status_code: int):
        message = f"Source '{address}' returned a server error (HTTP {status_code})."
        super().__init__(message)

class FetchTableNameNotProvidedError(FetchDbError):
    def __init__(self):
        message = "No table name provided as argument for fetching from database."
        super().__init__(message)

class FetchDbUrlNotFoundError(FetchDbError):
    def __init__(self, db_url: str):
        message = f"Source url '{db_url}' not found."
        super().__init__(message)

class FetchTableNotFoundError(FetchDbError):
    def __init__(self, table_name: str):
        message = f"Table '{table_name}' not found in database."
        super().__init__(message)

class FetchTableSerializationError(FetchDbError):
    def __init__(self, table_name: str):
        message = f"Content from '{table_name}' could not be serialized into JSON."
        super().__init__(message)

class DecodeError(FluxusError):
    """Errors occurring while decoding raw data (reading file format)."""

class DecodeMalformedError(DecodeError):
    """The file does not conform to the expected format (malformed CSV/XML/JSON)."""

class ExtractError(FluxusError):
    """Errors occurring while extracting decoded data into canonical form."""

class TransformError(FluxusError):
    """Errors occurring while transforming canonical data into the target format."""

class LoadError(FluxusError):
    """Errors occurring while writing to the target."""

class LoadTableNameNotProvidedError(LoadError):
    def __init__(self):
        message = "No table name provided as argument for inserting into the target database."
        super().__init__(message)

class LoadDbUrlNotFoundError(LoadError):
    def __init__(self, db_url: str):
        message = f"Target url '{db_url}' not found."
        super().__init__(message)

class LoadTableNotFoundError(LoadError):
    def __init__(self, table_name: str):
        message = f"Table '{table_name}' not found in the target database."
        super().__init__(message)

# --- Synchronic axis: organized by layer/technology, phase-independent ---

class SerializationError(FluxusError):
    """Errors occuring while serialization/type-conversion."""

class RegistryError(FluxusError):
    """Errors occurring while reading/writing the hash-based address registry."""

class RegistryEntryNotFoundError(RegistryError):
    """The requested registry entry does not exist or has been deactivated."""
    def __init__(
            self,*,
            entry_id: int | None = None,
            run_id:int |None = None,
            phase:Phase | None = None,
            content_hash:str | None = None
    ):
        no_id_msg = f"No active registry entry at address {entry_id}"
        no_hash_msg = f"No active registry entry with hash {content_hash}"
        no_run_id_msg = f"No active registry entry with run_id {run_id} at phase {phase} could be found."

        if entry_id:
            super().__init__(no_id_msg)
        elif content_hash:
            super().__init__(no_hash_msg)
        else:
            super().__init__(no_run_id_msg)

class InvalidRegistryEntryError(RegistryError):
    """The requested registry entry could not be validated."""
    def __init__(
            self,*,
            entry_id: int | None = None,
            run_id:int |None = None,
            phase:Phase | None = None,
            content_hash: str | None = None
    ):
        no_id_msg = f"Registry entry at address {entry_id} could not be validated."
        no_hash_msg = f"Registry entry with hash {content_hash} could not be validated."
        no_run_id_msg = f"Registry entry with run_id {run_id} at phase {phase} could not be validated."
        if entry_id:
            super().__init__(no_id_msg)
        elif content_hash:
            super().__init__(no_hash_msg)
        else:
            super().__init__(no_run_id_msg)

class StorageError(FluxusError):
    """Errors occurring while reading/writing payload data via a storage backend."""

class PayloadNotFoundError(StorageError):
    """The requested payload does not exist or has been deactivated."""