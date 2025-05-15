// models.ts

export class Product {
  id: number;
  name: string;
  type: string; // "raw" o "finished"

  constructor(data: any) {
    this.id = data.id;
    this.name = data.name;
    this.type = data.type;
  }
}

export class BOMItem {
  material_id: number;
  quantity: number;

  constructor(data: any) {
    this.material_id = data.material_id;
    this.quantity = data.quantity;
  }
}

export class BOM {
  id?: number;
  finished_product_id: number;
  components: BOMItem[];

  constructor(data: any) {
    this.id = data.id;
    this.finished_product_id = data.finished_product_id;
    this.components = (data.components || []).map((item: any) => new BOMItem(item));
  }
}

export class InventoryItem {
  product_id: number;
  quantity: number;

  constructor(data: any) {
    this.product_id = data.product_id;
    this.quantity = data.quantity;
  }
}

export class Supplier {
  id?: number;
  name: string;
  product_id: number;
  unit_cost: number;
  lead_time_days: number;

  constructor(data: any) {
    this.id = data.id;
    this.name = data.name;
    this.product_id = data.product_id;
    this.unit_cost = data.unit_cost;
    this.lead_time_days = data.lead_time_days;
  }
}

export class PurchaseOrder {
  id?: number;
  supplier_id: number;
  product_id: number;
  quantity: number;
  issue_date: string; // formato ISO
  expected_delivery_date: string; // formato ISO
  status: string;

  constructor(data: any) {
    this.id = data.id;
    this.supplier_id = data.supplier_id;
    this.product_id = data.product_id;
    this.quantity = data.quantity;
    this.issue_date = data.issue_date;
    this.expected_delivery_date = data.expected_delivery_date;
    this.status = data.status;
  }
}

export class ProductionOrder {
  id?: number;
  creation_date: string; // formato ISO
  product_id: number;
  quantity: number;
  status: string;

  constructor(data: any) {
    this.id = data.id;
    this.creation_date = data.creation_date;
    this.product_id = data.product_id;
    this.quantity = data.quantity;
    this.status = data.status;
  }
}

export class Event {
  id?: number;
  type: string;
  sim_date: number;
  detail: string;

  constructor(data: any) {
    this.id = data.id;
    this.type = data.type;
    this.sim_date = data.sim_date;
    this.detail = data.detail;
  }
}

export class DailyOrder {
  model: string;
  quantity: number;

  constructor(data: any) {
    this.model = data.model;
    this.quantity = data.quantity;
  }
}

export class DailyPlan {
  day: number;
  orders: DailyOrder[];

  constructor(data: any) {
    this.day = data.day;
    this.orders = (data.orders || []).map((item: any) => new DailyOrder(item));
  }
}

export class ModelBOM {
  bom: Record<string, number>;

  constructor(data: any) {
    this.bom = data.bom;
  }
}

export class SimulationConfig {
  capacity_per_day: number;
  models: Record<string, ModelBOM>;
  plan: DailyPlan[];

  constructor(data: any) {
    this.capacity_per_day = data.capacity_per_day;
    this.models = {};
    for (const key in data.models) {
      this.models[key] = new ModelBOM(data.models[key]);
    }
    this.plan = (data.plan || []).map((item: any) => new DailyPlan(item));
  }
}
