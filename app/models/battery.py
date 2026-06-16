from sqlalchemy import Column, Integer, Float
from app.database.database import Base


class BatteryStatus(Base):
    __tablename__ = "battery_status"

    id = Column(Integer, primary_key=True, index=True)
    battery_level = Column(Float, nullable=False)
    battery_voltage = Column(Float, nullable=False)
