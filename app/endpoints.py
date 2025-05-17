from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from production import add_to_production
from simulator import SimulationEngine
from database import get_session, Product as DBProduct, Inventory as DBInventory, \
    ProductionOrder as DBProductionOrder, PurchaseOrder as DBPurchaseOrder, Supplier as DBSupplier, Event as DBEvent, DailyPlan as DBDailyPlan, BOM as DBBOM
from model import Product, InventoryItem, ProductionOrder, PurchaseOrder, Supplier, Event, DailyPlan, BOMItem, \
    SimulationResponse
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/app", tags=["App"])

db = get_session()

# --- Endpoints de lectura con acceso a base de datos ---

@router.get("/inventory/", response_model=list[InventoryItem])
def get_inventory(session: Session = Depends(get_session)):
    inventory = session.query(DBInventory).all()
    return [InventoryItem(product_id=item.product_id, quantity=item.quantity) for item in inventory]

@router.get("/products/", response_model=list[Product])
def get_products(session: Session = Depends(get_session)):
    products = session.query(DBProduct).all()
    return [Product(id=p.id, name=p.name, type=p.type) for p in products]

@router.get("/production/orders/", response_model=list[ProductionOrder])
def get_production_orders(session: Session = Depends(get_session)):
    orders = session.query(DBProductionOrder).all()
    return [ProductionOrder(
        id=o.id, creation_date=o.creation_date,
        product_id=o.product_id, quantity=o.quantity, status=o.status,
        expected_completion_date=o.expected_completion_date
    ) for o in orders]

@router.get("/purchases/orders/", response_model=list[PurchaseOrder])
def get_purchase_orders(session: Session = Depends(get_session)):
    orders = session.query(DBPurchaseOrder).all()
    return [PurchaseOrder(
        id=o.id, supplier_id=o.supplier_id,
        product_id=o.product_id, quantity=o.quantity,
        issue_date=o.issue_date,
        expected_delivery_date=o.expected_delivery_date,
        status=o.status
    ) for o in orders]

@router.get("/suppliers/", response_model=list[Supplier])
def get_suppliers(session: Session = Depends(get_session)):
    suppliers = session.query(DBSupplier).all()
    return [Supplier(
        id=s.id, name=s.name,
        product_id=s.product_id,
        unit_cost=s.unit_cost,
        lead_time_days=s.lead_time_days
    ) for s in suppliers]

@router.get("/plan/", response_model=list[DailyPlan])
def get_plan(session: Session = Depends(get_session)):
    plans = session.query(DBDailyPlan).all()
    return [DailyPlan(
        id=p.id,
        day=p.day,
        orders=[{
            "model": p.model,
            "quantity": p.quantity,
            "status": p.status
        }]
    ) for p in plans]

@router.get("/events/", response_model=list[Event])
def get_events(session: Session = Depends(get_session)):
    events = session.query(DBEvent).all()
    return [Event(id=e.id, type=e.type, sim_date=e.sim_date, detail=e.detail) for e in events]


@router.get("/products/", response_model=list[Product])
def get_products(session: Session = Depends(get_session)):
    products = session.query(DBProduct).all()
    return [Product(id=p.id, name=p.name, type=p.type) for p in products]

@router.get("/status")
def get_status():
    return {"status": "OK", "day": 1}

@router.post("/import/json")
def import_from_json():
    return {"status": "imported"}

from fastapi import Body

@router.post("/products")
def create_product(product: Product = Body(...), session: Session = Depends(get_session)):
    db_product = DBProduct(name=product.name, type=product.type)
    session.add(db_product)
    try:
        session.commit()
        session.refresh(db_product)
        return Product(id=db_product.id, name=db_product.name, type=db_product.type)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="El producto ya existe (nombre duplicado).")

@router.post("/purchases/orders")
def create_purchase_order(order: PurchaseOrder, session: Session = Depends(get_session)):
    db_order = DBPurchaseOrder(
        supplier_id=order.supplier_id,
        product_id=order.product_id,
        quantity=order.quantity,
        issue_date=order.issue_date,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return PurchaseOrder(
        id=db_order.id,
        supplier_id=db_order.supplier_id,
        product_id=db_order.product_id,
        quantity=db_order.quantity,
        issue_date=db_order.issue_date,
        expected_delivery_date=db_order.expected_delivery_date,
        status=db_order.status
    )


@router.get("/bom/{product_id}", response_model=list[BOMItem])
def get_bom(product_id: int, session: Session = Depends(get_session)):
    rows = session.query(DBBOM).filter(DBBOM.finished_product_id == product_id).all()
    return [BOMItem(material_id=r.material_id, quantity=r.quantity) for r in rows]

@router.post("/bom/{product_id}/add")
def add_bom_item(product_id: int, item: BOMItem, session: Session = Depends(get_session)):
    row = DBBOM(finished_product_id=product_id, material_id=item.material_id, quantity=item.quantity)
    session.merge(row)
    session.commit()
    return {"status": "ok"}

@router.delete("/bom/{product_id}/remove/{material_id}")
def delete_bom_item(product_id: int, material_id: int, session: Session = Depends(get_session)):
    session.query(DBBOM).filter(
        DBBOM.finished_product_id == product_id,
        DBBOM.material_id == material_id
    ).delete()
    session.commit()
    return {"status": "ok"}

@router.get("/simulator/events/all", response_model=List[Event])
def get_all_events(session: Session = Depends(get_session)):
    """
    Return all simulation events stored in the database.
    """
    try:
        events = session.query(DBEvent).order_by(DBEvent.sim_date).all()
        return [
            Event(
                id=event.id,
                type=event.type,
                sim_date=event.sim_date,
                detail=event.detail
            )
            for event in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


_engine = None

def get_engine(session: Session) -> SimulationEngine:
    global _engine
    if _engine is None:
        _engine = SimulationEngine(session)
    return _engine

@router.post("/simulator/run", response_model=SimulationResponse)
def run_simulation(session: Session = Depends(get_session)):
    """
    Run one day of simulation and return the events that occurred.
    """
    try:
        engine = get_engine(session)
        engine.run_one_day()
        
        # Get events for the day that was just simulated
        events = session.query(DBEvent).filter_by(sim_date=engine.current_day - 1).all()
        events_data = [
            Event(
                id=event.id,
                type=event.type,
                sim_date=event.sim_date,
                detail=event.detail
            )
            for event in events
        ]
        
        return SimulationResponse(
            success=True,
            day=engine.current_day - 1,
            events=events_data
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/production/start/{order_id}")
def start_production(order_id: int, session: Session = Depends(get_session)):
    try:
        message = add_to_production(order_id, session)
        return {"result": message}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
