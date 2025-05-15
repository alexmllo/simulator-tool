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
            inventory = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
            
            # Check if adding the order quantity would exceed max capacity
            if inventory:
                if inventory.quantity + order.quantity > inventory.max_capacity:
                    # Reschedule the order for the next day
                    order.expected_delivery_date = day + 1
                    self.log_event(
                        "purchase_rescheduled",
                        day,
                        f"Pedido de compra #{order.id} reprogramado para el día {day + 1} - Capacidad máxima alcanzada"
                    )
                else:
                    inventory.quantity += order.quantity
                    order.status = "delivered"
                    self.log_event(
                        "purchase_arrival",
                        day,
                        f"Llegada de {order.quantity} unidades de {inventory.product.name} (OC #{order.id})"
                    )
            else:
                # For new inventory items, check if initial quantity exceeds max capacity
                if order.quantity > 1000:  # Default max capacity
                    # Reschedule the order for the next day
                    order.expected_delivery_date = day + 1
                    self.log_event(
                        "purchase_rescheduled",
                        day,
                        f"Pedido de compra #{order.id} reprogramado para el día {day + 1} - Capacidad máxima alcanzada"
                    )
                else:
                    self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))
                    order.status = "delivered"
                    self.log_event(
                        "purchase_arrival",
                        day,
                        f"Llegada de {order.quantity} unidades (OC #{order.id})"
                    )
            
            self.db.commit()


    def execute_production(self, day: int):
        """Execute production orders for today and complete orders"""
        yield self.env.timeout(0)
        
        # First, complete production orders
        completed_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "in_progress",
            ProductionOrder.expected_completion_date == day
        ).all()

        for order in completed_orders:
            product = self.db.query(Product).filter_by(id=order.product_id).first()
            
            # Add finished product to inventory
            inventory = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
            if inventory:
                if inventory.quantity + order.quantity > inventory.max_capacity:
                    # Reschedule the production completion for the next day
                    order.expected_completion_date = day + 1
                    self.log_event(
                        "production_rescheduled",
                        day,
                        f"Producción de {order.quantity} unidades de {product.name} reprogramada para el día {day + 1} - Capacidad máxima alcanzada"
                    )
                else:
                    inventory.quantity += order.quantity
                    order.status = "completed"
                    self.log_event(
                        "production_completed",
                        day,
                        f"Producción completada: {order.quantity} unidades de {product.name}"
                    )
            else:
                # For new inventory items
                self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))
                order.status = "completed"
                self.log_event(
                    "production_completed",
                    day,
                    f"Producción completada: {order.quantity} unidades de {product.name}"
                )

        # Then, start new production orders
        pending_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "pending",
        ).all()

        for order in pending_orders:
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
