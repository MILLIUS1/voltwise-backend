from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.battery import BatteryStatus
from app.schemas.battery import BatteryCreate, BatteryResponse

router = APIRouter(prefix="/battery", tags=["Battery"])


@router.post("/", response_model=BatteryResponse)
def update_battery(data: BatteryCreate, db: Session = Depends(get_db)):
    battery = BatteryStatus(**data.model_dump())

    db.add(battery)
    db.commit()
    db.refresh(battery)

    return battery


@router.get("/latest")
def get_latest_battery(db: Session = Depends(get_db)):
    latest = (
        db.query(BatteryStatus)
        .order_by(BatteryStatus.id.desc())
        .first()
    )

    if not latest:
        return {
            "battery_level": 0,
            "battery_voltage": 0
        }

    return latest
