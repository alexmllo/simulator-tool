from database import init_db
from import_service import import_simulation_from_json


init_db()
import_simulation_from_json("../data/plan.json")