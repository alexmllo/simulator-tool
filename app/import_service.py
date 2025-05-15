import json
from model import SimulationConfig
from database import get_session, Product, BOM, DailyPlan
from sqlalchemy.orm import Session
from sqlalchemy import and_

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
        # Insertar o actualizar producto terminado
        product = db.query(Product).filter_by(name=model_name).first()
        if not product:
            product = Product(name=model_name, type="finished")
            db.add(product)
            db.flush()
        else:
            product.type = "finished"
        product_ids[model_name] = product.id

        # Insertar o actualizar materias primas
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
                quantity=order.quantity
            ))

    db.commit()
    print("Importación completada.")
