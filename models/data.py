from datetime import datetime
from typing import TypeVar, Optional

from sqlmodel import SQLModel, Field, Relationship

from models.devices import Device
from models.locations import Location

T = TypeVar("T")


class EnvironmentData(SQLModel, table=True):
    __tablename__ = "environment_data"

    id: Optional[int] = Field(primary_key=True)
    device_id: int = Field(foreign_key="devices.id")
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    illuminance: Optional[int]
    location_id: Optional[int] = Field(foreign_key="locations.id")

    device_name_fk: Device =  Relationship(back_populates="data")
    location_name_fk: Location = Relationship(back_populates="data")