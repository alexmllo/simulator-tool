import simpy 
from database import get_session, Inventory, DailyPlan, Product, ProductionOrder, PurchaseOrder, Event 
from sqlalchemy.orm import Session 
from datetime import datetime, timedelta

class SimulationEngine:
  def init(self, db: Session): 
    self.env = simpy.Environment() 
    self.db = db 
    self.current_day = 0 
    self.capacity_per_day = 10 # esto luego puede venir de configuración

  def run_one_day(self):
    print(f"🕒 Ejecutando día {self.current_day}...")
    self.env.process(self.process_day(self.current_day))
    self.env.run(until=self.env.now + 1)
    self.current_day += 1

  def process_day(self, day: int):
      yield self.env.timeout(0)

      self.log_event("start_day", day, f"Inicio del día {day}")

      self.handle_arrivals(day)
      self.handle_plan_orders(day)
      self.execute_production(day)

      self.log_event("end_day", day, f"Fin del día {day}")

  def handle_arrivals(self, day: int):
      """Procesa entregas programadas para el día actual"""
      current_date = datetime.today().date() + timedelta(days=day)
      deliveries = self.db.query(PurchaseOrder).filter(
          PurchaseOrder.expected_delivery_date == current_date,
          PurchaseOrder.status == "pending"
      ).all()

      for order in deliveries:
          # Marcar como entregado
          order.status = "delivered"

          # Actualizar inventario
          inventory = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
          if inventory:
              inventory.quantity += order.quantity
          else:
              self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))

          # Log
          self.log_event(
              "purchase_arrival",
              day,
              f"Llegada de {order.quantity} unidades de producto ID {order.product_id} (OC #{order.id})"
          )

      self.db.commit()

  def handle_plan_orders(self, day: int):
      """Procesa los pedidos del plan del día"""
      plan_items = self.db.query(DailyPlan).filter_by(day=day).all()
      if not plan_items:
          self.log_event("plan_empty", day, f"No hay pedidos programados para el día {day}")
          return

      for item in plan_items:
          product = self.db.query(Product).filter_by(name=item.model, type="finished").first()
          if not product:
              self.log_event("error", day, f"Modelo '{item.model}' no encontrado como producto terminado")
              continue

          production_order = ProductionOrder(
              creation_date=datetime.today().date() + timedelta(days=day),
              product_id=product.id,
              quantity=item.quantity,
              status="pending"
          )
          self.db.add(production_order)

          self.log_event(
              "production_order",
              day,
              f"Orden de producción creada: {item.quantity} unidades de {item.model}"
          )

      self.db.commit()


  def execute_production(self, day: int):
      """Produce hasta agotar la capacidad"""
      capacity_left = self.capacity_per_day
      orders = self.db.query(ProductionOrder).filter_by(status="pending").order_by(ProductionOrder.id).all()

      for order in orders:
          if order.quantity > capacity_left:
              continue  # no cabe hoy

          # Cargar la BOM del producto
          bom_items = self.db.query(BOM).filter_by(finished_product_id=order.product_id).all()

          # Verificar disponibilidad de materias primas
          has_materials = True
          for bom in bom_items:
              stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
              required_qty = bom.quantity * order.quantity
              if not stock or stock.quantity < required_qty:
                  has_materials = False
                  self.log_event("error", day, f"Falta de stock para producto {bom.material_id}: se requieren {required_qty}")
                  break

          if not has_materials:
              continue

          # Descontar materiales
          for bom in bom_items:
              stock = self.db.query(Inventory).filter_by(product_id=bom.material_id).first()
              stock.quantity -= bom.quantity * order.quantity

          # Aumentar inventario del producto terminado
          finished = self.db.query(Inventory).filter_by(product_id=order.product_id).first()
          if finished:
              finished.quantity += order.quantity
          else:
              self.db.add(Inventory(product_id=order.product_id, quantity=order.quantity))

          # Marcar como completado
          order.status = "completed"
          capacity_left -= order.quantity

          # Log
          self.log_event("production_end", day, f"Producidas {order.quantity} unidades del producto ID {order.product_id}")

      self.db.commit()


  def log_event(self, type_: str, sim_date: int, detail: str):
      event = Event(
          type=type_,
          sim_date=sim_date,
          detail=detail
      )
      self.db.add(event)
      self.db.commit()
