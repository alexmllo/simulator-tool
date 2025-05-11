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
        
        # Check for unfulfilled plans from previous days
        yield self.env.process(self.handle_unfulfilled_plans(day))
        
        # Then handle the daily plan
        yield self.env.process(self.handle_daily_plan(day))
        
        # Finally, start production for next day
        yield self.env.process(self.start_production(day))

        self.log_event("end_day", day, f"Fin del día {day}")

    def handle_arrivals(self, day: int):
        """Process deliveries and completed production from previous day"""
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

        # Handle completed production from previous day
        completed_production = self.db.query(ProductionOrder).filter(
            ProductionOrder.expected_completion_date == day,
            ProductionOrder.status == "in_progress"
        ).all()

        for order in completed_production:
            order.status = "completed"
            product = self.db.query(Product).filter_by(id=order.product_id).first()
            
            # Add to inventory
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

        self.db.commit()

    def handle_unfulfilled_plans(self, day: int):
        """Check and process unfulfilled plans from previous days"""
        yield self.env.timeout(0)
        
        # Get all unfulfilled plans from previous days
        previous_plans = self.db.query(DailyPlan).filter(
            DailyPlan.day < day,
            DailyPlan.status == "pending"
        ).all()
        
        for plan in previous_plans:
            # Check if this plan has been fulfilled
            product = self.db.query(Product).filter_by(name=plan.model, type="finished").first()
            if not product:
                continue

            # Check current inventory
            inventory = self.db.query(Inventory).filter_by(product_id=product.id).first()
            stock_qty = inventory.quantity if inventory else 0

            if stock_qty >= plan.quantity:
                # We have enough stock, fulfill order
                inventory.quantity -= plan.quantity
                plan.status = "fulfilled"
                self.log_event(
                    "order_fulfilled",
                    day,
                    f"Pedido retrasado cumplido: {plan.quantity} unidades de {plan.model} del día {plan.day}"
                )
            else:
                # Check if we have materials to produce
                bom_items = self.db.query(BOM).filter_by(finished_product_id=product.id).all()
                has_materials = True
                missing_materials = []

                for bom in bom_items:
                    stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
                    required_qty = bom.quantity * plan.quantity
                    if not stock or stock.quantity < required_qty:
                        has_materials = False
                        missing_materials.append({
                            'material_id': bom.material_id,
                            'required_qty': required_qty,
                            'current_qty': stock.quantity if stock else 0
                        })

                if has_materials:
                    # Create production order for next day
                    production_order = ProductionOrder(
                        creation_date=day,
                        product_id=product.id,
                        quantity=plan.quantity,
                        status="pending",
                        expected_completion_date=day + 1
                    )
                    self.db.add(production_order)
                    self.log_event(
                        "production_order_created",
                        day,
                        f"Orden de producción creada para pedido retrasado: {plan.quantity} unidades de {plan.model} del día {plan.day}"
                    )
                else:
                    # Create purchase orders for missing materials
                    for missing in missing_materials:
                        material = self.db.query(Product).filter_by(id=missing['material_id']).first()
                        if material and material.type == "raw":
                            # Get the supplier for this material
                            supplier = self.db.query(Supplier).filter_by(product_id=material.id).first()
                            if not supplier:
                                self.log_event(
                                    "error",
                                    day,
                                    f"No se encontró proveedor para el material {material.name}"
                                )
                                continue

                            # Check if we already have a pending purchase order for this material and plan
                            existing_order = self.db.query(PurchaseOrder).filter(
                                PurchaseOrder.product_id == material.id,
                                PurchaseOrder.plan_id == plan.id,
                                PurchaseOrder.status == "pending"
                            ).first()

                            if existing_order:
                                continue

                            # Calculate quantity to order
                            qty_to_order = int(missing['required_qty'] - missing['current_qty'])

                            purchase_order = PurchaseOrder(
                                supplier_id=supplier.id,
                                product_id=material.id,
                                plan_id=plan.id,  # Link to the plan
                                quantity=qty_to_order,
                                issue_date=day,
                                expected_delivery_date=day + supplier.lead_time_days,
                                status="pending"
                            )
                            self.db.add(purchase_order)
                            self.log_event(
                                "purchase_order_created",
                                day,
                                f"Orden de compra creada para pedido retrasado: {qty_to_order} unidades del material {material.name} al proveedor {supplier.name} para el día {day + supplier.lead_time_days}"
                            )

        self.db.commit()

    def handle_daily_plan(self, day: int):
        """Process daily plan orders and create production orders if needed"""
        yield self.env.timeout(0)
        plan_items = self.db.query(DailyPlan).filter_by(day=day).all()
        
        if not plan_items:
            self.log_event("plan_empty", day, f"No hay pedidos programados para el día {day}")
            return

        for item in plan_items:
            product = self.db.query(Product).filter_by(name=item.model, type="finished").first()
            if not product:
                self.log_event("error", day, f"Modelo '{item.model}' no encontrado como producto terminado")
                continue

            # Check current inventory
            inventory = self.db.query(Inventory).filter_by(product_id=product.id).first()
            stock_qty = inventory.quantity if inventory else 0

            if stock_qty >= item.quantity:
                # We have enough stock, fulfill order
                inventory.quantity -= item.quantity
                item.status = "fulfilled"
                self.log_event(
                    "order_fulfilled",
                    day,
                    f"Pedido de {item.quantity} unidades de {item.model} cumplido desde inventario"
                )
            else:
                # Check if we have materials to produce
                bom_items = self.db.query(BOM).filter_by(finished_product_id=product.id).all()
                has_materials = True
                missing_materials = []

                for bom in bom_items:
                    stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
                    required_qty = bom.quantity * item.quantity
                    if not stock or stock.quantity < required_qty:
                        has_materials = False
                        missing_materials.append({
                            'material_id': bom.material_id,
                            'required_qty': required_qty,
                            'current_qty': stock.quantity if stock else 0
                        })

                if has_materials:
                    # Create production order for next day
                    production_order = ProductionOrder(
                        creation_date=day,
                        product_id=product.id,
                        quantity=item.quantity,
                        status="pending",
                        expected_completion_date=day + 1
                    )
                    self.db.add(production_order)
                    self.log_event(
                        "production_order_created",
                        day,
                        f"Orden de producción creada: {item.quantity} unidades de {item.model} para el día {day + 1}"
                    )
                else:
                    # Create purchase orders for missing materials
                    for missing in missing_materials:
                        material = self.db.query(Product).filter_by(id=missing['material_id']).first()
                        if material and material.type == "raw":
                            # Get the supplier for this material
                            supplier = self.db.query(Supplier).filter_by(product_id=material.id).first()
                            if not supplier:
                                self.log_event(
                                    "error",
                                    day,
                                    f"No se encontró proveedor para el material {material.name}"
                                )
                                continue

                            # Calculate quantity to order (current requirement + safety stock)
                            qty_to_order = missing['required_qty'] - missing['current_qty']
                            safety_stock = max(10, qty_to_order * 0.2)  # 20% safety stock or minimum 10 units
                            qty_to_order = int(qty_to_order + safety_stock)

                            purchase_order = PurchaseOrder(
                                supplier_id=supplier.id,
                                product_id=material.id,
                                quantity=qty_to_order,
                                issue_date=day,
                                plan_id=item.id,
                                expected_delivery_date=day + supplier.lead_time_days,
                                status="pending"
                            )
                            self.db.add(purchase_order)
                            self.log_event(
                                "purchase_order_created",
                                day,
                                f"Orden de compra creada: {qty_to_order} unidades del material {material.name} al proveedor {supplier.name} para el día {day + supplier.lead_time_days}"
                            )

        self.db.commit()

    def start_production(self, day: int):
        """Start production for next day's orders"""
        yield self.env.timeout(0)
        
        # Get pending production orders
        pending_orders = self.db.query(ProductionOrder).filter(
            ProductionOrder.status == "pending",
            ProductionOrder.expected_completion_date == day + 1
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
