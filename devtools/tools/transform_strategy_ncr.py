from pydantic import BaseModel, computed_field, model_validator
from pathlib import Path
from datetime import datetime
import json
from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData, TransformedData, Attachment


class Actor(BaseModel):
    name: str
    role: str
    institution: str


class Capa(BaseModel):
    corrective: bool
    preventive: bool
    action_description: str
    target_date: str
    responsibility: Actor
    status: str
    implemented_by: Actor | None
    implement_date: str | None
    verified_by: Actor | None
    verify_date: str | None
    evidence: str | None
    evidence_attachments: list[Attachment]


class CapaPlan(BaseModel):
    plan_no: str
    containment_action: str
    why_why: list[tuple[str, str]]
    root_cause: str
    capas: list[Capa]


class NCRDocument(BaseModel):
    ncr_no: str
    issue_date: str
    issuer: Actor
    occurance_site: str
    nc_description: str
    nc_attachments: list[Attachment]
    severity: str
    disposition: str
    capa_plans: list[CapaPlan]
    status: str
    closure_date: str | None
    closer: Actor


class TransformStrategyNCR:
    def __init__(
        self, *, target_format: ContentFormat, data: TransformableData, **kwargs
    ):
        self.target_format = target_format
        self.data = data

    def transform(self) -> TransformedData: ...
