from database import Base, engine, DB_PATH
import os
from import_service import import_initial_inventory_from_json, import_production_orders_from_json, import_providers_from_json, import_purchase_orders_from_json, import_simulation_from_json

def init_db():
    if not os.path.exists(DB_PATH):
        print("Inicializando base de datos...")
        Base.metadata.create_all(bind=engine)
        import_simulation_from_json("data/plan.json")
        import_providers_from_json("data/providers.json")
        import_initial_inventory_from_json("data/inventory_init.json")
        # import_production_orders_from_json("data/production_orders.json")
        # import_purchase_orders_from_json("data/purchase_orders.json")

    else:
        Base.metadata.create_all(bind=engine)