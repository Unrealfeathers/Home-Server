from typing import TypeVar, Optional

from sqlmodel import SQLModel, Field, Relationship

T = TypeVar("T")


class DeviceType(SQLModel, table=True):
    __tablename__ = "device_types"

    id: Optional[int] = Field(primary_key=True)
    name: str
    manufacturer: Optional[str] = Field(max_length=32)
    model: Optional[str] = Field(max_length=32)
    description: Optional[str]
    icon_url: Optional[str] = Field(max_length=255)
    capabilities: Optional[str]

    devices: list["Device"] = Relationship(back_populates="device_type")