from sqlalchemy import LargeBinary, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class FluxusDevSourceORM(DeclarativeBase):
    pass


class DevSourceDataText(FluxusDevSourceORM):
    __tablename__ = "dev_source_data_text"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(Text)


class DevSourceDataBlob(FluxusDevSourceORM):
    __tablename__ = "dev_source_data_blob"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)


class FluxusDevTargetORM(DeclarativeBase):
    pass


class DevTargetDataText(FluxusDevTargetORM):
    __tablename__ = "dev_target_data_text"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(Text)


class DevTargetDataBlob(FluxusDevTargetORM):
    __tablename__ = "dev_target_data_blob"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)
