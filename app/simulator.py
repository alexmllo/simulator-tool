from datetime import date, datetime, timedelta
import simpy 
import random
from database import Inventory, DailyPlan, Product, ProductionOrder, PurchaseOrder, Event, BOM, Supplier, SimulationState
from sqlalchemy.orm import Session 

class SimulationEngine:
    def __init__(self, db: Session): 
        self.env = simpy.Environment() 
        self.db = db 
        
        # Load current day from database
        state = self.db.query(SimulationState).first()
        if state:
            self.current_day = state.current_day
        else:
            # Initialize if not exists
            state = SimulationState(current_day=datetime.now().date())
            self.db.add(state)
            self.db.commit()
            self.current_day = datetime.now().date()
        
        self.capacity_per_day = 10
        self.min_daily_orders = 1  # Minimum number of orders per day
        self.max_daily_orders = 2  # Maximum number of orders per day
        self.min_order_quantity = 1  # Minimum quantity per order
        self.max_order_quantity = 10  # Maximum quantity per order

    def run_one_day(self):
        print(f"🕒 Ejecutando día {self.current_day}...")
        self.env.process(self.process_day(self.current_day))
        self.env.run()
        self.current_day = (self.current_day + timedelta(days=1))
        
        # Save current day to database
        state = self.db.query(SimulationState).first()
        state.current_day = self.current_day
        self.db.commit()

    def process_day(self, day: datetime):
        yield self.env.timeout(0)
        formatted_day = day.strftime("%d/%m/%Y")
        self.log_event("start_day", day, f"Inicio del día {formatted_day}")

        # First handle arrivals from previous day's production and purchases
        yield self.env.process(self.handle_arrivals(day))
        
        # Check if we need to generate a new plan
        yield self.env.process(self.check_and_generate_plan(day))
        
        # Then execute production orders for today
        yield self.env.process(self.execute_production(day))

        self.log_event("end_day", day, f"Fin del día {formatted_day}")

    def check_and_generate_plan(self, day: datetime):
        """Check if we need to generate a new plan for the next day"""
        yield self.env.timeout(0)
        
        tomorrow : date = (day + timedelta(days=1))
        # Check if we have a plan for tomorrow
        tomorrow_plan = self.db.query(DailyPlan).filter(
            DailyPlan.day == tomorrow
        ).first()
        if tomorrow_plan:
            return
            
        # Get all finished products
        finished_products = self.db.query(Product).filter_by(type="finished").all()
        if not finished_products:
            self.log_event("error", day, "No hay productos finales disponibles para generar plan")
            return
            
        # Generate random number of orders for tomorrow
        num_orders = random.randint(self.min_daily_orders, self.max_daily_orders)
        
        # Generate random orders
        for _ in range(num_orders):
            # Select random product
            product = random.choice(finished_products)
            
            # Generate random quantity
            quantity = random.randint(self.min_order_quantity, self.max_order_quantity)
            
            # Create daily plan entry
            plan = DailyPlan(
                day=tomorrow,
                model=product.name,
                quantity=quantity,
                status="pending"
            )
            self.db.add(plan)
            
        self.db.commit()
        self.log_event(
            "plan_generated",
            day,
            f"Plan generado para el día {day + timedelta(days=1)} con {num_orders} órdenes"
        )


    def handle_arrivals(self, day: datetime):
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
                    order.expected_delivery_date = day + timedelta(days=1)
                    self.log_event(
                        "purchase_rescheduled",
                        day,
                        f"Pedido de compra #{order.id} reprogramado para el día {day + timedelta(days=1)} - Capacidad máxima alcanzada"
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
                    order.expected_delivery_date = day + timedelta(days=1)
                    self.log_event(
                        "purchase_rescheduled",
                        day,
                        f"Pedido de compra #{order.id} reprogramado para el día {day + timedelta(days=1)} - Capacidad máxima alcanzada"
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


    def execute_production(self, day: datetime):
        """Execute production orders for today and complete orders"""
        yield self.env.timeout(0)
        
        # First, complete production orders in progress
        production_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "in_progress"
        ).all()

        for order in production_orders:
            product = self.db.query(Product).filter_by(id=order.product_id).first()
            
            order.status = "completed"
            # Find and update the corresponding daily plan using the direct relationship
            daily_plan = self.db.query(DailyPlan).filter_by(id=order.daily_plan_id).first()
            self.log_event(
                "production_completed",
                day,
                f"Producción completada: {order.quantity} unidades de {product.name}"
            )
            
            if daily_plan:
                daily_plan.status = "fulfilled"
                self.log_event(
                    "order_fulfilled",
                    day,
                    f"Pedido #{order.id} completado: {order.quantity} unidades de {product.name}"
                )

        # Then, start new production orders in pending
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


    def log_event(self, type_: str, sim_date: datetime, detail: str):
        try:
            formatted_date = sim_date.strftime("%d/%m/%Y")
            # Replace all product IDs with names in the detail
            if "producto" in detail:
                # Extract the product ID if it exists
                if "ID" in detail:
                    product_id = int(detail.split("ID ")[1].split()[0])
                elif "día" in detail:
                    detail = detail.replace(str(sim_date), formatted_date)
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
