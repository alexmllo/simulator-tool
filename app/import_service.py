import json
from model import SimulationConfig
from database import get_session, Product, BOM, DailyPlan, Supplier, Inventory, ProductionOrder, PurchaseOrder
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta, datetime

def import_simulation_from_json(json_path: str):
    # 1. Leer el archivo
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    # Convert dates from dd/mm/yyyy to yyyy-mm-dd format
    for plan in raw_data["plan"]:
        # Convert the day string to a date object
        day_str = plan["day"]
        day_obj = datetime.strptime(day_str, "%d/%m/%Y").date()
        plan["day"] = day_obj.isoformat()  # Convert to ISO format string
        plan["id"] = 0  # The database will assign the real ID
        for order in plan["orders"]:
            order["status"] = "pending"  # Set initial status

    # 2. Validar con Pydantic
    config = SimulationConfig(**raw_data)

    # 3. Guardar en la base de datos
    db: Session = get_session()

    print("Importando modelos y BOMs...")
    product_ids = {}

    for model_name, model_data in config.models.items():
        # Insertar producto terminado
        existing = db.query(Product).filter_by(name=model_name).first()
        if existing:
            product_ids[model_name] = existing.id
        else:
            product = Product(name=model_name, type="finished")
            db.add(product)
            db.flush()
            product_ids[model_name] = product.id

        # Insertar materias primas si no existen
        for material_name in model_data.bom:
            if material_name not in product_ids:
                existing = db.query(Product).filter_by(name=material_name).first()
                if existing:
                    product_ids[material_name] = existing.id
                else:
                    raw_product = Product(name=material_name, type="raw")
                    db.add(raw_product)
                    db.flush()
                    product_ids[material_name] = raw_product.id

        # Insertar BOMs
        for material_name, qty in model_data.bom.items():
            if not isinstance(qty, int):
                print(f"Ignorando '{material_name}': valor no entero ({qty})")
                continue

            if material_name not in product_ids:
                material = db.query(Product).filter_by(name=material_name).first()
                if not material:
                    material = Product(name=material_name, type="raw")
                    db.add(material)
                    db.flush()
                product_ids[material_name] = material.id

            # Eliminar BOM previa si existe
            db.query(BOM).filter(
                and_(
                    BOM.finished_product_id == product_ids[model_name],
                    BOM.material_id == product_ids[material_name]
                )
            ).delete()

            # Insertar BOM nueva
            bom = BOM(
                finished_product_id=product_ids[model_name],
                material_id=product_ids[material_name],
                quantity=qty
            )
            db.add(bom)

    print("Importando plan diario...")
    for plan in config.plan:
        for order in plan.orders:
            # Eliminar orden previa del mismo día y modelo si existe
            db.query(DailyPlan).filter(
                and_(
                    DailyPlan.day == plan.day,
                    DailyPlan.model == order.model
                )
            ).delete()

            db.add(DailyPlan(
                day=plan.day,
                model=order.model,
                quantity=order.quantity,
                status=order.status  # Add status when creating DailyPlan
            ))

    db.commit()
    print("Importación completada.")

def import_providers_from_json(json_path: str):
    """Import providers and their materials from providers.json"""
    with open(json_path, "r") as f:
        data = json.load(f)

    db: Session = get_session()
    print("Importando proveedores y materiales...")

    try:
        for provider_data in data["providers"]:
            # Create or get supplier
            supplier = Supplier(
                name=provider_data["name"]
            )
            db.add(supplier)
            db.flush()  # To get the supplier ID

            # Process each material for this supplier
            for material_name, material_info in provider_data["materials"].items():
                # Get or create the product
                product = db.query(Product).filter_by(name=material_name).first()
                if not product:
                    product = Product(name=material_name, type="raw")
                    db.add(product)
                    db.flush()

                # Create a new supplier entry for each material
                material_supplier = Supplier(
                    name=provider_data["name"],
                    product_id=product.id,
                    unit_cost=material_info["unit_cost"],
                    lead_time_days=material_info["lead_time_days"]
                )
                db.add(material_supplier)

        db.commit()
        print("✅ Proveedores importados correctamente")
    except Exception as e:
        print(f"❌ Error al importar proveedores: {e}")
        db.rollback()
        raise

def import_initial_inventory_from_json(json_path: str):
    """Import initial inventory levels from inventory_init.json"""
    with open(json_path, "r") as f:
        data = json.load(f)

    db: Session = get_session()
    print("Importando inventario inicial...")

    try:
        for material_name, quantity in data.items():
            # Get or create the product
            product = db.query(Product).filter_by(name=material_name).first()
            if not product:
                product = Product(name=material_name, type="raw")
                db.add(product)
                db.flush()

            # Create or update inventory
            inventory = db.query(Inventory).filter_by(product_id=product.id).first()
            if inventory:
                inventory.quantity = quantity
            else:
                inventory = Inventory(
                    product_id=product.id,
                    quantity=quantity
                )
                db.add(inventory)

        db.commit()
        print("✅ Inventario inicial importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar inventario inicial: {e}")
        db.rollback()
        raise

def import_production_orders_from_json(json_path: str):
    """Import production orders from production_orders.json"""
    with open(json_path, "r") as f:
        data = json.load(f)

    db: Session = get_session()
    print("Importando órdenes de producción...")

    try:
        for order_data in data["orders"]:
            # Get the product
            product = db.query(Product).filter_by(name=order_data["product"]).first()
            if not product:
                raise Exception(f"Producto no encontrado: {order_data['product']}")

            # Convert dd/mm/yyyy strings to date objects
            creation_date = datetime.strptime(order_data["creation_date"], "%d/%m/%Y").date()
            expected_completion_date = datetime.strptime(order_data["expected_completion_date"], "%d/%m/%Y").date()

            # Create production order
            production_order = ProductionOrder(
                creation_date=creation_date,
                product_id=product.id,
                quantity=order_data["quantity"],
                status=order_data["status"],
                expected_completion_date=expected_completion_date
            )
            db.add(production_order)

        db.commit()
        print("✅ Órdenes de producción importadas correctamente")
    except Exception as e:
        print(f"❌ Error al importar órdenes de producción: {e}")
        db.rollback()
        raise

def import_purchase_orders_from_json(json_path: str):
    """Import purchase orders from purchase_orders.json"""
    with open(json_path, "r") as f:
        data = json.load(f)

    db: Session = get_session()
    print("Importando órdenes de compra...")

    try:
        for order_data in data["orders"]:
            # Get the supplier and product
            supplier = db.query(Supplier).filter_by(name=order_data["supplier"]).first()
            product = db.query(Product).filter_by(name=order_data["product"]).first()
            
            if not supplier:
                raise Exception(f"Proveedor no encontrado: {order_data['supplier']}")
            if not product:
                raise Exception(f"Producto no encontrado: {order_data['product']}")

            # Create purchase order
            purchase_order = PurchaseOrder(
                supplier_id=supplier.id,
                product_id=product.id,
                quantity=order_data["quantity"],
                issue_date=order_data["issue_date"],
                expected_delivery_date=order_data["expected_delivery_date"],
                status=order_data["status"]
            )
            db.add(purchase_order)

        db.commit()
        print("✅ Órdenes de compra importadas correctamente")
    except Exception as e:
        print(f"❌ Error al importar órdenes de compra: {e}")
        db.rollback()
        raise
