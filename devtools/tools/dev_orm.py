from sqlalchemy import LargeBinary, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class PluggleDevSourceORM(DeclarativeBase):
    pass


class DevSourceDataText(PluggleDevSourceORM):
    __tablename__ = "dev_source_data_text"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(Text)


class DevSourceDataBlob(PluggleDevSourceORM):
    __tablename__ = "dev_source_data_blob"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)


class PluggleDevTargetORM(DeclarativeBase):
    pass


class DevTargetDataText(PluggleDevTargetORM):
    __tablename__ = "dev_target_data_text"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(Text)


class DevTargetDataBlob(PluggleDevTargetORM):
    __tablename__ = "dev_target_data_blob"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)
