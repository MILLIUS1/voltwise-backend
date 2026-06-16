from enum import Enum
from pydantic import BaseModel


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ApplianceCreate(BaseModel):
    name: str
    power_rating: float
    priority: Priority
    status: bool = True


class ApplianceUpdate(BaseModel):
    name: str
    power_rating: float
    priority: Priority
    status: bool


class ApplianceResponse(BaseModel):
    id: int
    name: str
    power_rating: float
    priority: str
    status: bool

    class Config:
        from_attributes = True
