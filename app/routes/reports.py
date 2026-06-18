from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.appliance import Appliance
from app.models.energy import EnergyReading

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
def reports_summary(db: Session = Depends(get_db)):
    total_energy = db.query(func.coalesce(func.sum(EnergyReading.power_consumed), 0)).scalar()
    peak_usage = db.query(func.coalesce(func.max(EnergyReading.power_consumed), 0)).scalar()
    average_usage = db.query(func.coalesce(func.avg(EnergyReading.power_consumed), 0)).scalar()
    readings_count = db.query(EnergyReading).count()

    return {
        "total_energy": float(total_energy),
        "peak_usage": float(peak_usage),
        "average_usage": float(average_usage),
        "readings_count": readings_count,
        "estimated_savings": round(float(total_energy) * 0.21, 2),
    }


@router.get("/appliance-breakdown")
def appliance_breakdown(db: Session = Depends(get_db)):
    results = (
        db.query(
            Appliance.name,
            func.coalesce(func.sum(EnergyReading.power_consumed), 0).label("total_usage"),
        )
        .outerjoin(EnergyReading, Appliance.id == EnergyReading.appliance_id)
        .group_by(Appliance.id, Appliance.name)
        .order_by(func.coalesce(func.sum(EnergyReading.power_consumed), 0).desc())
        .all()
    )

    total = sum(float(row.total_usage) for row in results)

    return [
        {
            "name": row.name,
            "usage": float(row.total_usage),
            "percentage": round((float(row.total_usage) / total * 100), 1) if total > 0 else 0,
        }
        for row in results
    ]


@router.get("/daily")
def daily_report(db: Session = Depends(get_db)):
    readings = (
        db.query(EnergyReading)
        .order_by(EnergyReading.timestamp.asc())
        .all()
    )

    data = []
    for reading in readings:
        data.append({
            "time": reading.timestamp.strftime("%H:%M"),
            "usage": float(reading.power_consumed),
            "appliance_id": reading.appliance_id,
        })

    return data
