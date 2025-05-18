from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import DailyPlan, Product, BOM, Inventory, ProductionOrder, SimulationState

def add_to_production(order_id: int, session: Session):
    """
    Add a daily plan order to production if we have enough materials.
    Returns a message: str
    """
    try:
        # Get the order from daily plan
        order = session.query(DailyPlan).filter_by(id=order_id).first()
        if not order:
            return "Order not found"

        # Get the product
        product = session.query(Product).filter_by(name=order.model).first()
        if not product:
            return f"Product {order.model} not found"

        # Get BOM for the product
        bom_items = session.query(BOM).filter_by(finished_product_id=product.id).all()
        if not bom_items:
            return f"No BOM found for product {order.model}"

        # Check inventory for each material
        missing_materials = []
        for bom_item in bom_items:
            inventory = session.query(Inventory).filter_by(product_id=bom_item.material_id).first()
            required_quantity = bom_item.quantity * order.quantity
            
            if not inventory or inventory.quantity < required_quantity:
                material = session.query(Product).filter_by(id=bom_item.material_id).first()
                missing_materials.append(f"{material.name}: {required_quantity - (inventory.quantity if inventory else 0)} units")

        if missing_materials:
            return f"Missing materials: {', '.join(missing_materials)}"

        # Get current simulation day
        state = session.query(SimulationState).first()
        current_day = state.current_day if state else datetime.now().date()

        # Create production order
        production_order = ProductionOrder(
            creation_date=current_day,
            product_id=product.id,
            quantity=order.quantity,
            status="pending",
            expected_completion_date=current_day + timedelta(days=1),
            daily_plan_id=order_id
        )
        session.add(production_order)
        
        # Update daily plan status to in_production
        order.status = "in_production"
        
        # Remove raw materials from inventory
        for bom_item in bom_items:
            inventory = session.query(Inventory).filter_by(product_id=bom_item.material_id).first()
            required_quantity = bom_item.quantity * order.quantity
            inventory.quantity -= required_quantity
        
        session.commit()
        return "ok"

    except Exception as e:
        session.rollback()
        return str(e)
