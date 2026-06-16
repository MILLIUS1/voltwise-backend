from datetime import datetime
from pydantic import BaseModel


class EnergyReadingCreate(BaseModel):
    appliance_id: int
    power_consumed: float


class EnergyReadingResponse(BaseModel):
    id: int
    appliance_id: int
    power_consumed: float
    timestamp: datetime

    class Config:
        from_attributes = True
