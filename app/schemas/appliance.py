from typing import Optional
from pydantic import BaseModel


class ApplianceUpdate(BaseModel):
    name: Optional[str] = None
    power_rating: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[bool] = None
