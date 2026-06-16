from pydantic import BaseModel


class BatteryCreate(BaseModel):
    battery_level: float
    battery_voltage: float


class BatteryResponse(BaseModel):
    id: int
    battery_level: float
    battery_voltage: float

    class Config:
        from_attributes = True
