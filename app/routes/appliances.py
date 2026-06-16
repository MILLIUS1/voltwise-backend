from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.appliance import Appliance
from app.schemas.appliance import ApplianceCreate, ApplianceUpdate, ApplianceResponse

router = APIRouter(prefix="/appliances", tags=["Appliances"])


@router.post("/", response_model=ApplianceResponse)
def create_appliance(appliance: ApplianceCreate, db: Session = Depends(get_db)):
    new_appliance = Appliance(**appliance.model_dump())
    db.add(new_appliance)
    db.commit()
    db.refresh(new_appliance)
    return new_appliance


@router.get("/", response_model=list[ApplianceResponse])
def get_appliances(db: Session = Depends(get_db)):
    return db.query(Appliance).all()


@router.get("/{appliance_id}", response_model=ApplianceResponse)
def get_appliance(appliance_id: int, db: Session = Depends(get_db)):
    appliance = db.query(Appliance).filter(Appliance.id == appliance_id).first()

    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    return appliance


@router.put("/{appliance_id}", response_model=ApplianceResponse)
def update_appliance(appliance_id: int, appliance_data: ApplianceUpdate, db: Session = Depends(get_db)):
    appliance = db.query(Appliance).filter(Appliance.id == appliance_id).first()

    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    appliance.name = appliance_data.name
    appliance.power_rating = appliance_data.power_rating
    appliance.priority = appliance_data.priority
    appliance.status = appliance_data.status

    db.commit()
    db.refresh(appliance)

    return appliance


@router.delete("/{appliance_id}")
def delete_appliance(appliance_id: int, db: Session = Depends(get_db)):
    appliance = db.query(Appliance).filter(Appliance.id == appliance_id).first()

    if not appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")

    db.delete(appliance)
    db.commit()

    return {"message": "Appliance deleted successfully"}
