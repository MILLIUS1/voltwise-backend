from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.models.battery import BatteryStatus
from app.models.grid import GridStatus
from app.models.settings import SystemSetting

router = APIRouter(prefix="/decision", tags=["Decision Engine"])


@router.post("/apply")
def apply_decision(db: Session = Depends(get_db)):
    latest_grid = db.query(GridStatus).order_by(GridStatus.id.desc()).first()
    latest_battery = db.query(BatteryStatus).order_by(BatteryStatus.id.desc()).first()
    settings = db.query(SystemSetting).order_by(SystemSetting.id.desc()).first()
    appliances = db.query(Appliance).all()

    if not latest_grid or not latest_battery:
        return {"message": "Grid or battery data missing", "actions": []}

    conservation = settings.conservation_threshold if settings else 80
    critical = settings.critical_threshold if settings else 40
    reserve = settings.reserve_level if settings else 30

    actions = []
    battery_level = latest_battery.battery_level
    grid_available = latest_grid.is_available

    if grid_available:
        for appliance in appliances:
            if appliance.status is False:
                appliance.status = True
                actions.append(f"Restored {appliance.name}")
        mode = "GRID_RESTORED"

    else:
        if battery_level <= reserve:
            mode = "EMERGENCY_RESERVE_MODE"
            allowed_priorities = ["HIGH"]
        elif battery_level <= critical:
            mode = "CRITICAL_POWER_MODE"
            allowed_priorities = ["HIGH"]
        elif battery_level <= conservation:
            mode = "BATTERY_CONSERVATION_MODE"
            allowed_priorities = ["HIGH", "MEDIUM"]
        else:
            mode = "BATTERY_BACKUP_MODE"
            allowed_priorities = ["HIGH", "MEDIUM", "LOW"]

        for appliance in appliances:
            priority = appliance.priority.upper()
            if priority not in allowed_priorities and appliance.status is True:
                appliance.status = False
                actions.append(f"Disconnected {appliance.name}")

    db.commit()

    return {
        "mode": mode,
        "grid_available": grid_available,
        "battery_level": battery_level,
        "conservation_threshold": conservation,
        "critical_threshold": critical,
        "reserve_level": reserve,
        "actions": actions,
    }


@router.get("/status")
def decision_status(db: Session = Depends(get_db)):
    latest_grid = db.query(GridStatus).order_by(GridStatus.id.desc()).first()
    latest_battery = db.query(BatteryStatus).order_by(BatteryStatus.id.desc()).first()
    settings = db.query(SystemSetting).order_by(SystemSetting.id.desc()).first()

    if not latest_grid or not latest_battery:
        return {"message": "Grid or battery data missing"}

    conservation = settings.conservation_threshold if settings else 80
    critical = settings.critical_threshold if settings else 40
    reserve = settings.reserve_level if settings else 30

    battery_level = latest_battery.battery_level
    grid_available = latest_grid.is_available

    if grid_available:
        mode = "GRID_AVAILABLE"
    elif battery_level <= reserve:
        mode = "EMERGENCY_RESERVE_MODE"
    elif battery_level <= critical:
        mode = "CRITICAL_POWER_MODE"
    elif battery_level <= conservation:
        mode = "BATTERY_CONSERVATION_MODE"
    else:
        mode = "BATTERY_BACKUP_MODE"

    return {
        "mode": mode,
        "grid_available": grid_available,
        "battery_level": battery_level,
        "conservation_threshold": conservation,
        "critical_threshold": critical,
        "reserve_level": reserve,
    }
