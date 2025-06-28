from datetime import datetime

from pydantic import BaseModel, ConfigDict

class DataList(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    device_name: str
    timestamp: datetime
    temperature: float
    humidity: float
    illuminance: int
    location_name: str

class Command(BaseModel):
    command: str
