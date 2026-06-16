from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

from app.database.database import get_db
from app.models.energy import EnergyReading
from app.models.appliance import Appliance
from app.schemas.energy import EnergyReadingCreate, EnergyReadingResponse

router = APIRouter(prefix="/energy", tags=["Energy Monitoring"])


@router.post("/readings", response_model=EnergyReadingResponse)
def create_energy_reading(reading: EnergyReadingCreate, db: Session = Depends(get_db)):
    appliance = db.query(Appliance).filter(Appliance.id == reading.appliance_id).first()

    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    new_reading = EnergyReading(**reading.model_dump())
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


@router.get("/readings", response_model=list[EnergyReadingResponse])
def get_energy_readings(db: Session = Depends(get_db)):
    return db.query(EnergyReading).all()


@router.get("/current")
def get_current_usage(db: Session = Depends(get_db)):
    latest = db.query(EnergyReading).order_by(EnergyReading.timestamp.desc()).first()

    if not latest:
        return {"current_usage": 0}

    return {"current_usage": latest.power_consumed}


@router.get("/daily")
def get_daily_usage(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()

    total = db.query(func.sum(EnergyReading.power_consumed)).filter(
        func.date(EnergyReading.timestamp) == today
    ).scalar()

    return {"daily_consumption": total or 0}


@router.get("/monthly")
def get_monthly_usage(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    total = db.query(func.sum(EnergyReading.power_consumed)).filter(
        func.extract("year", EnergyReading.timestamp) == now.year,
        func.extract("month", EnergyReading.timestamp) == now.month
    ).scalar()

    return {"monthly_consumption": total or 0}
