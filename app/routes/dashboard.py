from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.grid import GridStatus
from app.models.battery import BatteryStatus
from app.models.energy import EnergyReading
from app.models.appliance import Appliance
from app.models.alert import Alert

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard(db: Session = Depends(get_db)):
    grid = db.query(GridStatus).order_by(GridStatus.id.desc()).first()
    battery = db.query(BatteryStatus).order_by(BatteryStatus.id.desc()).first()
    alert = db.query(Alert).order_by(Alert.id.desc()).first()

    current_reading = db.query(EnergyReading).order_by(
        EnergyReading.id.desc()
    ).first()

    today_usage = db.query(
        func.sum(EnergyReading.power_consumed)
    ).scalar() or 0

    active = db.query(Appliance).filter(
        Appliance.status == True
    ).count()

    total = db.query(Appliance).count()

    return {
        "grid_status": grid.is_available if grid else False,
        "battery_level": battery.battery_level if battery else 0,
        "current_usage": current_reading.power_consumed if current_reading else 0,
        "active_appliances": active,
        "total_appliances": total,
        "today_energy_usage": today_usage,
        "latest_alert": alert.message if alert else "No alerts"
    }
