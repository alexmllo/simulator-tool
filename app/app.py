from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import Event, get_session, init_db
from import_service import import_initial_inventory_from_json, import_providers_from_json, import_simulation_from_json
from simulator import SimulationEngine

app = FastAPI(title="Supply Chain Simulator API")

# Initialize database and import initial data
init_db()
import_simulation_from_json("data/plan.json")
import_providers_from_json("data/providers.json")
import_initial_inventory_from_json("data/inventory_init.json")

# Pydantic models
class EventResponse(BaseModel):
    type: str
    sim_date: int
    detail: str

class SimulationResponse(BaseModel):
    success: bool
    day: int
    events: List[EventResponse]
    error: Optional[str] = None

@app.post("/api/simulator/run", response_model=SimulationResponse)
async def run_simulation():
    """
    Run one day of simulation and return the events that occurred.
    """
    try:
        db = get_session()
        engine = SimulationEngine(db)
        engine.run_one_day()
        
        # Get events for the day that was just simulated
        events = db.query(Event).filter_by(sim_date=engine.current_day - 1).all()
        events_data = [
            EventResponse(
                type=event.type,
                sim_date=event.sim_date,
                detail=event.detail
            )
            for event in events
        ]
        
        return SimulationResponse(
            success=True,
            day=engine.current_day - 1,
            events=events_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

