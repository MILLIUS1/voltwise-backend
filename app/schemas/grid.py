from pydantic import BaseModel


class GridCreate(BaseModel):
    is_available: bool
    voltage: float
    frequency: float


class GridResponse(BaseModel):
    id: int
    is_available: bool
    voltage: float
    frequency: float

    class Config:
        from_attributes = True
