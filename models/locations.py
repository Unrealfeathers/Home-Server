from typing import TypeVar, Optional

from sqlmodel import SQLModel, Field, Relationship

T = TypeVar("T")


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    id: Optional[int] = Field(primary_key=True)
    name: str
    description: Optional[str]

    devices: list["Device"] = Relationship(back_populates="location")

    data: list["EnvironmentData"] = Relationship(back_populates="location_name_fk")