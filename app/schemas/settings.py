from pydantic import BaseModel


class SettingsCreate(BaseModel):
    conservation_threshold: float = 50
    critical_threshold: float = 20
    reserve_level: float = 10
    notifications_enabled: bool = True
    dark_mode_enabled: bool = False


class SettingsResponse(SettingsCreate):
    id: int

    class Config:
        from_attributes = True
