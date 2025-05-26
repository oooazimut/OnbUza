from datetime import datetime
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

dttm = Annotated[datetime, mapped_column(default=datetime.now)]
classic_id = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Pump(Base):
    __tablename__ = "pumps"

    id: Mapped[classic_id]
    name: Mapped[str]
    pressure: Mapped[float]
    temperature: Mapped[float]
    dttm: Mapped[dttm]

    def __repr__(self) -> str:
        return f"Pump(id={self.id!r}, name={self.name!r}, pressure={self.pressure!r}, temperature={self.temperature!r}, dttm={self.dttm!r})"


class Gas_Sensor(Base):
    __tablename__ = "gas_sensors"

    id: Mapped[classic_id]
    name: Mapped[str]
    value: Mapped[float]
    dttm: Mapped[dttm]

    def __repr__(self) -> str:
        return f"Gas_Sensor(id={self.id!r}, value={self.value!r}, dttm={self.dttm!r})"
