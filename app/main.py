from database import init_db
from import_service import import_simulation_from_json
from simulator import SimulationEngine
from database import get_session

init_db()
import_simulation_from_json("data/plan.json")

db = get_session()
engine = SimulationEngine(db)
engine.run_one_day()