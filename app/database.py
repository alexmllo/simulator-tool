from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, ForeignKey, Table, Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

Base = declarative_base()
DB_PATH = "data/simulator.db"
DB_FILE = "sqlite:///"+DB_PATH

engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# --- MODELOS ---

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String)  # 'raw' or 'finished'

    inventory_items = relationship("Inventory", back_populates="product")


class BOM(Base):
    __tablename__ = "bom"
    id = Column(Integer, primary_key=True, index=True)
    finished_product_id = Column(Integer, ForeignKey("product.id"))
    material_id = Column(Integer, ForeignKey("product.id"))
    quantity = Column(Integer, nullable=False)


class SimulationState(Base):
    __tablename__ = "simulation_state"
    id = Column(Integer, primary_key=True)
    current_day = Column(Integer, default=1)


class Inventory(Base):
    __tablename__ = "inventory"
    product_id = Column(Integer, ForeignKey("product.id"), primary_key=True)
    quantity = Column(Integer, default=0)
    max_capacity = Column(Integer, default=1000)
    product = relationship("Product", back_populates="inventory_items")


class Supplier(Base):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    product_id = Column(Integer, ForeignKey("product.id"))
    unit_cost = Column(Float)
    lead_time_days = Column(Integer)


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("supplier.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    plan_id = Column(Integer, ForeignKey("daily_plan.id"))  # Link to the plan this purchase is for
    quantity = Column(Integer)
    issue_date = Column(Integer)
    expected_delivery_date = Column(Integer)
    status = Column(String)  # pending, delivered, cancelled


class ProductionOrder(Base):
    __tablename__ = "production_order"
    id = Column(Integer, primary_key=True, index=True)
    creation_date = Column(Integer)
    product_id = Column(Integer, ForeignKey("product.id"))
    quantity = Column(Integer)
    status = Column(String)  # pending, in_progress, completed, cancelled
    expected_completion_date = Column(Integer)


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    sim_date = Column(Integer)
    detail = Column(Text)


class DailyPlan(Base):
    __tablename__ = "daily_plan"
    id = Column(Integer, primary_key=True, index=True)
    day = Column(Integer)
    model = Column(String)
    quantity = Column(Integer)
    status = Column(String, default="pending")  # pending, fulfilled, cancelled


def get_session():
    return SessionLocal()

