from pydantic import BaseModel, computed_field, model_validator, Field
from pathlib import Path
from datetime import datetime
from fluxus.enums import FluxusIOType, ContentFormat, Phase, MimeType


class InputArgs(BaseModel):
    model_config = {"frozen": True}
    source_type: FluxusIOType
    source_address: str
    source_table: str | None
    transform_strategy_id: int
    target_type: FluxusIOType
    target_address: str
    target_table: str | None
    target_format: ContentFormat = ContentFormat.JSON

    @computed_field
    @property
    def source_as_path(self) -> Path:
        if self.source_type == FluxusIOType.FILE:
            return Path(self.source_address)
        else:
            raise AttributeError

    @computed_field
    @property
    def source_as_string(self) -> str:
        if self.source_type in (FluxusIOType.DB, FluxusIOType.API):
            return self.source_address
        else:
            raise AttributeError

    @computed_field
    @property
    def target_as_path(self) -> Path:
        if self.target_type == FluxusIOType.FILE:
            return Path(self.target_address)
        else:
            raise AttributeError

    @computed_field
    @property
    def target_as_string(self) -> str:
        if self.target_type in (FluxusIOType.DB, FluxusIOType.API):
            return self.target_address
        else:
            raise AttributeError

    @model_validator(mode="after")
    def check_table_names(self):
        if self.source_type == FluxusIOType.DB and self.source_table is None:
            raise ValueError("source_table is required when source_type is 'db'")
        if self.target_type == FluxusIOType.DB and self.target_table is None:
            raise ValueError("target_table is required when target_type is 'db'")
        return self


class RegistryRecord(BaseModel):
    model_config = {"frozen": True}
    id: int
    run_id: int
    phase: Phase
    content_format: ContentFormat
    strategy_name: str
    content_hash: str
    address: str
    created_at: datetime
    is_active: bool


class ExtractableData(BaseModel):
    model_config = {"frozen": True}
    content: bytes
    source_format: ContentFormat


class TransformableData(BaseModel):
    model_config = {"frozen": True}
    content: bytes
    origin_format: ContentFormat


class TransformedData(BaseModel):
    model_config = {"frozen": True}
    content: bytes
