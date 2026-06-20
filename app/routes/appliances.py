from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.models.grid import GridStatus
from app.models.battery import BatteryStatus
from app.schemas.appliance import ApplianceUpdate

router = APIRouter(prefix="/appliances", tags=["Appliances"])


def is_allowed_to_turn_on(priority: str, battery_level: float) -> bool:
    priority = priority.upper()

    if battery_level <= 10:
        return priority == "HIGH"

    if battery_level <= 20:
        return priority == "HIGH"

    if battery_level <= 50:
        return priority in ["HIGH", "MEDIUM"]

    return True


def get_latest_grid_available(db: Session) -> bool:
    latest_grid = db.query(GridStatus).order_by(GridStatus.id.desc()).first()

    if not latest_grid:
        return True

    return latest_grid.is_available is True


def get_latest_battery_level(db: Session) -> float:
    latest_battery = db.query(BatteryStatus).order_by(BatteryStatus.id.desc()).first()

    if not latest_battery:
        return 100

    return latest_battery.battery_level


@router.get("/")
def get_appliances(db: Session = Depends(get_db)):
    return db.query(Appliance).all()


@router.get("")
def get_appliances_no_slash(db: Session = Depends(get_db)):
    return db.query(Appliance).all()


@router.patch("/{appliance_id}")
def update_appliance(
    appliance_id: int,
    update: ApplianceUpdate,
    db: Session = Depends(get_db)
):
    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id
    ).first()

    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    if update.name is not None:
        appliance.name = update.name

    if update.power_rating is not None:
        appliance.power_rating = update.power_rating

    if update.priority is not None:
        appliance.priority = update.priority.upper()

    if update.status is not None:
        if update.status:
            grid_available = get_latest_grid_available(db)

            if grid_available:
                appliance.status = True
            else:
                battery_level = get_latest_battery_level(db)
                appliance.status = is_allowed_to_turn_on(
                    str(appliance.priority),
                    battery_level
                )
        else:
            appliance.status = False

    db.commit()
    db.refresh(appliance)

    return appliance
