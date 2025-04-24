from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session 
from database import get_session 
from simulator import SimulationEngine 

router = APIRouter()

def get_engine(): 
  db = get_session() 
  return SimulationEngine(db)

@router.post("/sim/advance-day") 
def advance_one_day(engine: SimulationEngine = Depends(get_engine)): 
  engine.run_one_day() 
  return { "message": "Día simulado", "day": engine.current_day + 1}