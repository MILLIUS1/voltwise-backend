from sqlalchemy import Column, Integer, Boolean, Float
from app.database.database import Base


class GridStatus(Base):
    __tablename__ = "grid_status"

    id = Column(Integer, primary_key=True, index=True)
    is_available = Column(Boolean, nullable=False)
    voltage = Column(Float, nullable=False)
    frequency = Column(Float, nullable=False)
