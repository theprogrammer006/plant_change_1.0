from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .crud import get_plants, get_plant
from .models import Plant
from .database import SessionLocal

app = FastAPI()

# In-memory storage for the currently selected plant thresholds
current_thresholds = {}

class PlantSelection(BaseModel):
    plant_id: int

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/plants")
async def read_plants(db: Session = Depends(get_db)):
    plants = get_plants(db)
    return plants

@app.post("/select_plant")
async def select_plant(selection: PlantSelection, db: Session = Depends(get_db)):
    plant = get_plant(db, selection.plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")

    # Store the selected plant's thresholds in memory
    global current_thresholds
    current_thresholds = {
        "light_threshold_min": plant.light_threshold_min,
        "light_threshold_max": plant.light_threshold_max,
        "temperature_threshold_min": plant.temperature_threshold_min,
        "temperature_threshold_max": plant.temperature_threshold_max,
        "moisture_threshold_min": plant.moisture_threshold_min,
        "moisture_threshold_max": plant.moisture_threshold_max,
    }

    return {"message": "Thresholds updated successfully", "thresholds": current_thresholds}

@app.get("/current_thresholds")
async def get_current_thresholds():
    if not current_thresholds:
        raise HTTPException(status_code=404, detail="No plant selected")
    return current_thresholds
