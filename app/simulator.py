import simpy 
from database import Inventory, DailyPlan, Product, ProductionOrder, PurchaseOrder, Event, BOM, Supplier
from sqlalchemy.orm import Session 

class SimulationEngine:
    def __init__(self, db: Session): 
        self.env = simpy.Environment() 
        self.db = db 
        self.current_day = 1
        self.capacity_per_day = 10

    def run_one_day(self):
        print(f"🕒 Ejecutando día {self.current_day}...")
        self.env.process(self.process_day(self.current_day))
        self.env.run()
        self.current_day += 1

    def process_day(self, day: int):
        yield self.env.timeout(0)
        self.log_event("start_day", day, f"Inicio del día {day}")

        # First handle arrivals from previous day's production and purchases
        yield self.env.process(self.handle_arrivals(day))
        
        # Then execute production orders for today
        yield self.env.process(self.execute_production(day))

        self.log_event("end_day", day, f"Fin del día {day}")

    def handle_arrivals(self, day: int):
        """Process deliveries from previous day's purchases"""
        yield self.env.timeout(0)
        
        # Handle purchase order arrivals
        deliveries = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.expected_delivery_date == day,
            PurchaseOrder.status == "pending"
        ).all()

        for order in deliveries:
            order.status = "delivered"
            inventory = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
            if inventory:
                inventory.quantity += order.quantity
            else:
                self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))
            
            self.log_event(
                "purchase_arrival",
                day,
                f"Llegada de {order.quantity} unidades de producto ID {order.product_id} (OC #{order.id})"
            )

        self.db.commit()

    def execute_production(self, day: int):
        """Execute production orders for today and complete orders from previous day"""
        yield self.env.timeout(0)
        
        # First, complete production orders from previous day
        completed_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "in_progress",
            ProductionOrder.expected_completion_date == day
        ).all()

        for order in completed_orders:
            order.status = "completed"
            product = self.db.query(Product).filter_by(id=order.product_id).first()
            
            # Add finished product to inventory
            inventory = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
            if inventory:
                inventory.quantity += order.quantity
            else:
                self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))
            
            self.log_event(
                "production_completed",
                day,
                f"Producción completada: {order.quantity} unidades de {product.name}"
            )

        # Then, start new production orders for today
        pending_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "pending",
            ProductionOrder.expected_completion_date == day + 1  # Orders started today complete tomorrow
        ).all()

        for order in pending_orders:
            # Check if we have all required materials
            bom_items = self.db.query(BOM).filter_by(finished_product_id=order.product_id).all()
            has_materials = True
            
            for bom in bom_items:
                stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
                required_qty = bom.quantity * order.quantity
                if not stock or stock.quantity < required_qty:
                    has_materials = False
                    self.log_event(
                        "error",
                        day,
                        f"Falta de materiales para producir {order.quantity} unidades del producto {order.product_id}"
                    )
                    break

            if has_materials:
                # Consume materials
                for bom in bom_items:
                    stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
                    stock.quantity -= bom.quantity * order.quantity

                # Mark order as in progress
                order.status = "in_progress"
                self.log_event(
                    "production_started",
                    day,
                    f"Iniciada producción de {order.quantity} unidades del producto {order.product_id}"
                )

        self.db.commit()

    def log_event(self, type_: str, sim_date: int, detail: str):
        try:
            # Replace all product IDs with names in the detail
            if "producto" in detail:
                # Extract the product ID if it exists
                if "ID" in detail:
                    product_id = int(detail.split("ID ")[1].split()[0])
                else:
                    # Handle cases where ID is just a number
                    words = detail.split()
                    for i, word in enumerate(words):
                        if word.isdigit() and i > 0 and words[i-1] == "producto":
                            product_id = int(word)
                            break
                    else:
                        product_id = None

                if product_id:
                    # Get the product name
                    product = self.db.query(Product).filter_by(id=product_id).first()
                    if product:
                        # Replace the ID with the name
                        if "ID" in detail:
                            detail = detail.replace(f"ID {product_id}", product.name)
                        else:
                            detail = detail.replace(f"producto {product_id}", f"producto {product.name}")

            event = Event(
                type=type_,
                sim_date=sim_date,
                detail=detail
            )
            self.db.add(event)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error al guardar evento: {type_} | Día: {sim_date} | Detalle: {detail}")
            print(f"Excepción original: {e}")
            self.db.rollback()
            raise
