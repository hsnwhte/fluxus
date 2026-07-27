from fluxus.enums import Phase
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, CHAR, Enum as SQLEnum, LargeBinary, String, ForeignKey


class FluxusORM(DeclarativeBase):
    pass

class PipelineRunRecord(FluxusORM):
    __tablename__="pipeline_runs"
    run_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class RegistryEntry(FluxusORM):
    __tablename__ = "registry"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column
    phase: Mapped[Phase] = mapped_column(SQLEnum(Phase))
    strategy_name:Mapped[str]=mapped_column(String(50))
    content_hash : Mapped[str] = mapped_column(CHAR(64), index=True)
    address: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(default=True)

class FetchCache(FluxusORM):
    __tablename__="fetch_cache"
    content_hash: Mapped[str] = mapped_column(CHAR(64), primary_key=True)
    address: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(default=True)


class PayloadRecord(FluxusORM):
    __tablename__ = "payloads"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phase: Mapped[Phase] = mapped_column(SQLEnum(Phase))
    payload: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)