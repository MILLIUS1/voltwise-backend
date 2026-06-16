from datetime import datetime
from pydantic import BaseModel


class AlertCreate(BaseModel):
    title: str
    message: str
    severity: str


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    timestamp: datetime

    class Config:
        from_attributes = True
