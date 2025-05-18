from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# --- Productos e Inventario ---

class Product(BaseModel):
    id: Optional[int]
    name: str
    type: str  # "raw" o "finished"


class BOMItem(BaseModel):
    material_id: int
    quantity: int


class BOM(BaseModel):
    id: Optional[int]
    finished_product_id: int
    components: List[BOMItem]  # para crear desde la API (no almacenado tal cual en la BD)


class InventoryItem(BaseModel):
    product_id: int
    quantity: int


# --- Proveedores y compras ---

class Supplier(BaseModel):
    id: Optional[int]
    name: str
    product_id: int
    unit_cost: float
    lead_time_days: int


class PurchaseOrder(BaseModel):
    id: Optional[int]
    supplier_id: int
    product_id: int
    quantity: int
    issue_date: date
    expected_delivery_date: date
    status: str  # "pending", "delivered", "cancelled"


# --- Producción y pedidos ---

class ProductionOrder(BaseModel):
    id: Optional[int]
    creation_date: date
    product_id: int
    quantity: int
    status: str  # "pending", "in_progress", "completed", "cancelled"
    expected_completion_date: date
    daily_plan_id: Optional[int]


# --- Evento registrado durante la simulación ---

class Event(BaseModel):
    id: Optional[int]
    type: str  # "production_start", etc.
    sim_date: date
    detail: str


# --- Configuración de la simulación (solo en memoria o JSON) ---

class ModelBOM(BaseModel):
    bom: dict[str, int]  # producto -> cantidad


class DailyOrder(BaseModel):
    model: str
    quantity: int
    status: str


class DailyPlan(BaseModel):
    id: int
    day: date
    orders: List[DailyOrder]


class SimulationConfig(BaseModel):
    capacity_per_day: int
    models: dict[str, ModelBOM]
    plan: List[DailyPlan]



class SimulationResponse(BaseModel):
    success: bool
    day: date
    events: List[Event]
    error: Optional[str] = None
