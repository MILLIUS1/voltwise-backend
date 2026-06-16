from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.grid import GridStatus
from app.schemas.grid import GridCreate, GridResponse

router = APIRouter(prefix="/grid", tags=["Grid Status"])


@router.post("/", response_model=GridResponse)
def update_grid_status(data: GridCreate, db: Session = Depends(get_db)):
    grid = GridStatus(**data.model_dump())

    db.add(grid)
    db.commit()
    db.refresh(grid)

    return grid


@router.get("/latest")
def get_latest_grid_status(db: Session = Depends(get_db)):
    latest = db.query(GridStatus).order_by(GridStatus.id.desc()).first()

    if not latest:
        return {
            "is_available": False,
            "voltage": 0,
            "frequency": 0
        }

    return latest
