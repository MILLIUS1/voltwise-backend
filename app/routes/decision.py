from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.models.battery import BatteryStatus
from app.models.grid import GridStatus
from app.models.settings import SystemSetting
from app.models.alert import Alert

router = APIRouter(prefix="/decision", tags=["Decision Engine"])


def calculate_decision(db: Session):
    grid = db.query(GridStatus).order_by(GridStatus.id.desc()).first()
    battery = db.query(BatteryStatus).order_by(BatteryStatus.id.desc()).first()
    settings = db.query(SystemSetting).order_by(SystemSetting.id.desc()).first()
    appliances = db.query(Appliance).all()

    grid_available = grid.is_available if grid else False
    battery_level = battery.battery_level if battery else 0

    conservation = settings.conservation_threshold if settings else 50
    critical = settings.critical_threshold if settings else 20
    reserve = settings.reserve_level if settings else 10

    if grid_available:
        mode = "NORMAL_OPERATION"
        action = "Grid power available. All appliances allowed."
        allowed_priorities = ["HIGH", "MEDIUM", "LOW"]
    elif battery_level > conservation:
        mode = "BATTERY_NORMAL"
        action = "Battery level is sufficient. All appliances allowed."
        allowed_priorities = ["HIGH", "MEDIUM", "LOW"]
    elif battery_level > critical:
        mode = "CONSERVATION_MODE"
        action = "Low-priority appliances disconnected."
        allowed_priorities = ["HIGH", "MEDIUM"]
    elif battery_level > reserve:
        mode = "CRITICAL_MODE"
        action = "Only high-priority appliances remain ON."
        allowed_priorities = ["HIGH"]
    else:
        mode = "RESERVE_MODE"
        action = "Emergency reserve mode. Only protected high-priority loads remain ON."
        allowed_priorities = ["HIGH"]

    return mode, action, grid_available, battery_level, conservation, critical, reserve, allowed_priorities


@router.post("/apply")
def apply_decision(db: Session = Depends(get_db)):
    mode, action, grid_available, battery_level, conservation, critical, reserve, allowed_priorities = calculate_decision(db)

    appliances = db.query(Appliance).all()
    disconnected = []

    for appliance in appliances:
        should_be_on = appliance.priority in allowed_priorities

        if appliance.status is True and should_be_on is False:
            disconnected.append(appliance.name)
            db.add(Alert(
                title="Appliance Disconnected",
                message=f"{appliance.name} was disconnected because the system entered {mode}.",
                severity="WARNING"
            ))

        appliance.status = should_be_on

    db.commit()

    return {
        "message": "Decision applied successfully",
        "mode": mode,
        "action": action,
        "grid_available": grid_available,
        "battery_level": battery_level,
        "disconnected_appliances": disconnected
    }


@router.get("/status")
def decision_status(db: Session = Depends(get_db)):
    mode, action, grid_available, battery_level, conservation, critical, reserve, allowed_priorities = calculate_decision(db)

    appliances = db.query(Appliance).all()
    active_appliances = []
    shed_appliances = []

    for appliance in appliances:
        should_be_on = appliance.priority in allowed_priorities

        item = {
            "id": appliance.id,
            "name": appliance.name,
            "priority": appliance.priority,
            "power_rating": appliance.power_rating,
            "current_status": appliance.status,
            "recommended_status": should_be_on
        }

        if should_be_on:
            active_appliances.append(item)
        else:
            shed_appliances.append(item)

    return {
        "mode": mode,
        "action": action,
        "grid_available": grid_available,
        "battery_level": battery_level,
        "thresholds": {
            "conservation_threshold": conservation,
            "critical_threshold": critical,
            "reserve_level": reserve
        },
        "active_appliances": active_appliances,
        "shed_appliances": shed_appliances
    }
