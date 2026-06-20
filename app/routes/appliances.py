from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.schemas.appliance import ApplianceUpdate

router = APIRouter(prefix="/appliances", tags=["Appliances"])


def is_allowed_to_turn_on(priority: str, battery_level: int) -> bool:
    priority = priority.upper()

    if battery_level <= 10:
        return priority == "HIGH"

    if battery_level <= 20:
        return priority == "HIGH"

    if battery_level <= 50:
        return priority in ["HIGH", "MEDIUM"]

    return True


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

    battery_level = 10

    if update.name is not None:
        appliance.name = update.name

    if update.power_rating is not None:
        appliance.power_rating = update.power_rating

    if update.priority is not None:
        appliance.priority = update.priority.upper()

    if update.status is not None:
        if update.status:
            appliance.status = is_allowed_to_turn_on(
                str(appliance.priority),
                battery_level
            )
        else:
            appliance.status = False

    db.commit()
    db.refresh(appliance)

    return appliance
