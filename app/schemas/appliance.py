from typing import Optional
from pydantic import BaseModel


class ApplianceBase(BaseModel):
    name: str
    power_rating: float
    priority: str
    status: bool = True


class ApplianceCreate(ApplianceBase):
    pass


class ApplianceUpdate(BaseModel):
    name: Optional[str] = None
    power_rating: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[bool] = None


class ApplianceResponse(ApplianceBase):
    id: int

    class Config:
        from_attributes = True
