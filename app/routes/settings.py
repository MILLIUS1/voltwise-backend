from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.settings import SystemSetting
from app.schemas.settings import SettingsCreate, SettingsResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/", response_model=SettingsResponse)
def save_settings(data: SettingsCreate, db: Session = Depends(get_db)):
    settings = db.query(SystemSetting).order_by(SystemSetting.id.desc()).first()

    if not settings:
        settings = SystemSetting(**data.model_dump())
        db.add(settings)
    else:
        settings.conservation_threshold = data.conservation_threshold
        settings.critical_threshold = data.critical_threshold
        settings.reserve_level = data.reserve_level
        settings.notifications_enabled = data.notifications_enabled
        settings.dark_mode_enabled = data.dark_mode_enabled

    db.commit()
    db.refresh(settings)
    return settings


@router.get("/latest", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSetting).order_by(SystemSetting.id.desc()).first()

    if not settings:
        settings = SystemSetting()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings
