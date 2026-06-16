from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

from app.database.database import get_db
from app.models.energy import EnergyReading
from app.models.appliance import Appliance
from app.models.alert import Alert

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/daily")
def daily_report(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()

    total = db.query(func.sum(EnergyReading.power_consumed)).filter(
        func.date(EnergyReading.timestamp) == today
    ).scalar() or 0

    peak = db.query(func.max(EnergyReading.power_consumed)).filter(
        func.date(EnergyReading.timestamp) == today
    ).scalar() or 0

    alerts_count = db.query(Alert).filter(
        func.date(Alert.timestamp) == today
    ).count()

    return {
        "period": "daily",
        "total_consumption": total,
        "peak_usage": peak,
        "average_usage": round(total / 24, 2),
        "estimated_savings": round(total * 0.21, 2),
        "estimated_savings_percent": 21,
        "automations_executed": alerts_count
    }


@router.get("/monthly")
def monthly_report(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    total = db.query(func.sum(EnergyReading.power_consumed)).filter(
        func.extract("year", EnergyReading.timestamp) == now.year,
        func.extract("month", EnergyReading.timestamp) == now.month
    ).scalar() or 0

    peak = db.query(func.max(EnergyReading.power_consumed)).filter(
        func.extract("year", EnergyReading.timestamp) == now.year,
        func.extract("month", EnergyReading.timestamp) == now.month
    ).scalar() or 0

    alerts_count = db.query(Alert).filter(
        func.extract("year", Alert.timestamp) == now.year,
        func.extract("month", Alert.timestamp) == now.month
    ).count()

    return {
        "period": "monthly",
        "total_consumption": total,
        "peak_usage": peak,
        "average_usage": round(total / 30, 2),
        "estimated_savings": round(total * 0.21, 2),
        "estimated_savings_percent": 21,
        "automations_executed": alerts_count
    }


@router.get("/appliance-breakdown")
def appliance_breakdown(db: Session = Depends(get_db)):
    results = (
        db.query(
            Appliance.name,
            func.sum(EnergyReading.power_consumed).label("total_usage")
        )
        .join(EnergyReading, EnergyReading.appliance_id == Appliance.id)
        .group_by(Appliance.name)
        .all()
    )

    total_all = sum(float(row.total_usage or 0) for row in results)

    breakdown = []
    for row in results:
        usage = float(row.total_usage or 0)
        percent = round((usage / total_all) * 100, 2) if total_all > 0 else 0

        breakdown.append({
            "appliance_name": row.name,
            "total_usage": usage,
            "percentage": percent
        })

    return breakdown


@router.get("/system-summary")
def system_summary(db: Session = Depends(get_db)):
    total_appliances = db.query(Appliance).count()
    active_appliances = db.query(Appliance).filter(Appliance.status == True).count()
    total_alerts = db.query(Alert).count()

    latest_reading = db.query(EnergyReading).order_by(EnergyReading.id.desc()).first()
    current_usage = latest_reading.power_consumed if latest_reading else 0

    return {
        "total_appliances": total_appliances,
        "active_appliances": active_appliances,
        "inactive_appliances": total_appliances - active_appliances,
        "current_usage": current_usage,
        "total_alerts": total_alerts
    }
