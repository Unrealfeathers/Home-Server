from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field

T = TypeVar("T")


class DeviceUpload(BaseModel, Generic[T]):
    status_code: int
    # todo
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    serial_number: str = Field(max_length=36)
    message: Optional[T] = Field(default=None)


class LTHData(BaseModel):
    lux: int
    temp: float
    humi: float


class DeviceAdd(BaseModel):
    name: str = Field(max_length=32)
    type_id: int
    serial_number: str = Field(max_length=36)
    mac_address: str = Field(max_length=32)
    firmware_version: str = Field(max_length=16)
    location_id: int


class DeviceUpdate(BaseModel):
    id: int
    name: str = Field(max_length=32)
    location_id: Optional[int]

class DeviceSearch(BaseModel):
    type_id: Optional[int] = Field(default=None)
    location_id: Optional[int] = Field(default=None)
    is_online: Optional[bool] = Field(default=None)

class DeviceList(BaseModel):
    id: int
    name: str
    type_name: str
    location_name: str
    mac_address: str
    serial_number: str
    firmware_version: str
    created_at: datetime
    is_online: bool
    last_online: datetime

class DeviceStatusList(DeviceList):
    status: str
    operation: str

class DeviceStatusUpdate(BaseModel):
    serial_number: str = Field(max_length=36)
    firmware_version: Optional[str] = Field(max_length=16)
    is_online: bool = Field(default=False)
