from typing import Protocol
from fluxus.enums import Phase
from fluxus.models.dto import RegistryRecord

class PipelineRunRecordsProtocol(Protocol):
    def register_run(self) -> int:
        """Persists content, returns an address referencing it."""
        ...

    def get_run_id(self, *, run_id: str) -> int:
        """Retrieves content previously stored at the given address."""
        ...


class RegistryStoreProtocol(Protocol):
    def save_entry(self, *, run_id:int, phase:Phase, strategy_name:str, content_hash:str, address:str) ->int:
        """Persists info from pipeline processors at successive phases."""
        ...

    def get_entry_by_id(self, *, id:int) -> RegistryRecord:
        """Retreives entry object by id"""
        ...

    def get_entry_by_run_id(self, *, run_id:int, phase:Phase) -> RegistryRecord:
        """Retreives entry object by run_id and phase"""
        ...

    def get_entry_by_hash(self, *, content_hash:str) -> RegistryRecord:
        """Retreives entry object by content hash"""
        ...

class PayloadStoreProtocol(Protocol):
    def save(self, *, phase:Phase, payload:bytes) -> str:
        """Persists content, returns an address referencing it."""
        ...
    def load(self, *, address:str) -> bytes:
        """Retrieves content previously stored at the given address."""
        ...