from database import init_db, Event, DailyPlan, Product
from import_service import import_simulation_from_json, import_providers_from_json, import_initial_inventory_from_json
from simulator import SimulationEngine
from database import get_session

def print_daily_plan(db, day):
    """Print the daily plan for a specific day"""
    plan_items = db.query(DailyPlan).filter_by(day=day).all()
    print(f"\n📋 Plan del día {day}:")
    print("=" * 50)
    if not plan_items:
        print("No hay pedidos programados para este día.")
    else:
        for item in plan_items:
            print(f"• {item.quantity} unidades de {item.model}")
    print("=" * 50)

def print_day_events(db, day):
    """Print all events for a specific day"""
    events = db.query(Event).filter_by(sim_date=day).order_by(Event.id).all()
    print(f"\n📅 Eventos del día {day}:")
    print("=" * 50)
    if not events:
        print("No hay eventos registrados para este día.")
    else:
        for event in events:
            print(f"• {event.detail}")
    print("=" * 50)

def main():
    # Initialize database and import data
    init_db()
    import_simulation_from_json("data/plan.json")
    import_providers_from_json("data/providers.json")
    import_initial_inventory_from_json("data/inventory_init.json")

    db = get_session()
    engine = SimulationEngine(db)
    
    current_day = 1
    while True:
        # Print daily plan before running the simulation
        print_daily_plan(db, current_day)
        
        # Run the simulation for the current day
        engine.run_one_day()
        
        # Print events for the current day
        print_day_events(db, current_day)
        
        # Ask if user wants to continue
        while True:
            response = input("\n¿Desea simular el siguiente día? (s/n): ").lower()
            if response in ['s', 'n']:
                break
            print("Por favor, responda 's' para sí o 'n' para no.")
        
        if response == 'n':
            print("\nSimulación finalizada.")
            break
            
        current_day += 1

if __name__ == "__main__":
    main()