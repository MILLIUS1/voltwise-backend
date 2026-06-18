from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.models.battery import BatteryStatus
from app.models.grid import GridStatus
from app.models.settings import SystemSetting
from app.models.alert import Alert

router = APIRouter(prefix="/decision", tags=["Decision Engine"])


def create_alert(db: Session, title: str, message: str, severity: str):
    alert = Alert(
        title=title,
        message=message,
        severity=severity,
    )
    db.add(alert)


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
        mode = "GRID_RESTORED"

        create_alert(
            db,
            "Grid Power Restored",
            "Grid power is available. VoltWise restored eligible appliances.",
            "INFO",
        )

        for appliance in appliances:
            if appliance.status is False:
                appliance.status = True
                action = f"Restored {appliance.name}"
                actions.append(action)

                create_alert(
                    db,
                    "Appliance Restored",
                    f"{appliance.name} has been restored after grid power returned.",
                    "INFO",
                )

    else:
        create_alert(
            db,
            "Grid Power Failure",
            "Grid supply is unavailable. VoltWise switched to battery backup mode.",
            "WARNING",
        )

        if battery_level <= reserve:
            mode = "EMERGENCY_RESERVE_MODE"
            allowed_priorities = ["HIGH"]

            create_alert(
                db,
                "Emergency Reserve Mode",
                f"Battery level reached {battery_level}%. Only high-priority appliances remain powered.",
                "CRITICAL",
            )

        elif battery_level <= critical:
            mode = "CRITICAL_POWER_MODE"
            allowed_priorities = ["HIGH"]

            create_alert(
                db,
                "Critical Power Mode",
                f"Battery level reached {battery_level}%. Low and medium priority appliances are disconnected.",
                "CRITICAL",
            )

        elif battery_level <= conservation:
            mode = "BATTERY_CONSERVATION_MODE"
            allowed_priorities = ["HIGH", "MEDIUM"]

            create_alert(
                db,
                "Battery Conservation Mode",
                f"Battery level reached {battery_level}%. Low-priority appliances are disconnected.",
                "WARNING",
            )

        else:
            mode = "BATTERY_BACKUP_MODE"
            allowed_priorities = ["HIGH", "MEDIUM", "LOW"]

            create_alert(
                db,
                "Battery Backup Mode",
                f"Grid is unavailable. Battery backup is active at {battery_level}%.",
                "INFO",
            )

        for appliance in appliances:
            priority = appliance.priority.upper()

            if priority not in allowed_priorities and appliance.status is True:
                appliance.status = False
                action = f"Disconnected {appliance.name}"
                actions.append(action)

                create_alert(
                    db,
                    "Appliance Disconnected",
                    f"{appliance.name} was disconnected because it is {priority} priority.",
                    "WARNING",
                )

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
