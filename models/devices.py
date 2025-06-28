from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.device_types import DeviceType
from models.locations import Location


class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: Optional[int] = Field(primary_key=True)
    name: str = Field(max_length=32)
    type_id: int = Field(foreign_key="device_types.id")
    serial_number: str = Field(max_length=36)
    mac_address: str = Field(max_length=32)
    firmware_version: Optional[str] = Field(max_length=16)
    created_at: datetime
    last_online: Optional[datetime]
    is_online: bool = Field(default=False)
    location_id: Optional[int] = Field(foreign_key="locations.id")

    location: Location = Relationship(back_populates="devices")
    device_type: DeviceType = Relationship(back_populates="devices")

    data: list["EnvironmentData"] = Relationship(back_populates="device_name_fk")
