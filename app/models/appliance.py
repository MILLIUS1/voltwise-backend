from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database.database import Base


class Appliance(Base):
    __tablename__ = "appliances"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    power_rating = Column(Float, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(Boolean, default=True)
