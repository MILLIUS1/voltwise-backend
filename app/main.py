from fastapi import FastAPI

from app.database.database import Base, engine

from app.models import (
    user,
    appliance,
    energy as energy_model,
    battery as battery_model,
    grid as grid_model,
    settings as settings_model,
    alert as alert_model,
)

from app.routes import (
    auth,
    appliances,
    energy,
    battery,
    grid,
    decision,
    settings,
    alerts,
    reports,
    dashboard,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VoltWise Backend")

app.include_router(auth.router)
app.include_router(appliances.router)
app.include_router(energy.router)
app.include_router(battery.router)
app.include_router(grid.router)
app.include_router(settings.router)
app.include_router(decision.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "VoltWise Backend is running"}
