from database import init_db
from import_service import import_simulation_from_json

from fastapi import FastAPI 
from sim import router as sim_router


init_db()
import_simulation_from_json("data/plan.json")

app = FastAPI() 
app.include_router(sim_router)