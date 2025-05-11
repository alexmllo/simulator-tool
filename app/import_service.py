import json
from model import SimulationConfig
from database import get_session, Product, BOM, DailyPlan, Supplier, Inventory
from sqlalchemy.orm import Session

def import_simulation_from_json(json_path: str):
    # 1. Leer el archivo
    with open(json_path, "r") as f:
        raw_data = json.load(f)

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
            bom = BOM(
                finished_product_id=product_ids[model_name],
                material_id=product_ids[material_name],
                quantity=qty
            )
            db.add(bom)

    print("Importando plan diario...")
    for plan in config.plan:
        for order in plan.orders:
            db.add(DailyPlan(
                day=plan.day,
                model=order.model,
                quantity=order.quantity
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
