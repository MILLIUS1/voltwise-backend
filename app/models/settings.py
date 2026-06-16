from sqlalchemy import Column, Integer, Float, Boolean
from app.database.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    conservation_threshold = Column(Float, default=50)
    critical_threshold = Column(Float, default=20)
    reserve_level = Column(Float, default=10)
    notifications_enabled = Column(Boolean, default=True)
    dark_mode_enabled = Column(Boolean, default=False)
