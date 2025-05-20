import { Component, OnInit } from '@angular/core';
import {HttpService} from '../../services/httpService';
import {Product, PurchaseOrder, Supplier} from '../../classes/models';

@Component({
  selector: 'app-panel-compras',
  standalone:false,
  templateUrl: './panel-compras.component.html',
  styleUrl: './panel-compras.component.css'
})
export class PanelComprasComponent implements OnInit {
  ordenesCompra: PurchaseOrder[] = [];
  productosRaw: Product[] = [];
  productosMap: Map<number, string> = new Map();
  suppliers: Supplier[] = [];
  uniqueSuppliers: Supplier[] = [];
  currentDay: Date = new Date();

  constructor(private http: HttpService) {}

  ngOnInit() {
    this.loadData();
    this.getCurrentDay();
  }

  loadData() {
    this.http.getOrdenesCompra((ordenes: PurchaseOrder[]) => {
      this.ordenesCompra = ordenes;
    });

    this.http.getProductos((productos) => {
      this.productosRaw = productos.filter(p => p.type === 'raw');
      productos.forEach(p => this.productosMap.set(p.id, p.name));
    });

    this.http.getSuppliers((suppliers) => {
      this.suppliers = suppliers;
      const uniqueMap = new Map<string, Supplier>();
      suppliers.forEach(supplier => {
        if (!uniqueMap.has(supplier.name)) {
          uniqueMap.set(supplier.name, supplier);
        }
      });
      this.uniqueSuppliers = Array.from(uniqueMap.values());
    });
  }

  getCurrentDay() {
    this.http.getCurrentDay((response) => {
      this.currentDay = new Date(response.current_day);
      this.nuevaCompra.issue_date = this.currentDay;
    });
  }

  getProviderName(id: number): string {
    const supplier = this.suppliers.find(s => s.id === id);
    return supplier ? supplier.name : `#${id}`;
  }

  getNombreProducto(id: number): string {
    return this.productosMap.get(id) || `#${id}`;
  }

  nuevaCompra = new PurchaseOrder({
    supplier_id: 0,
    product_id: 0,
    quantity: 0,
    issue_date: new Date(),
    expected_delivery_date: new Date(),
    status: 'pending'
  });

  submitCompra() {
    console.log('Form submitted with values:', this.nuevaCompra);
    
    if (!this.nuevaCompra.supplier_id || !this.nuevaCompra.product_id || !this.nuevaCompra.expected_delivery_date) {
      alert('Por favor, complete todos los campos requeridos');
      return;
    }
    else if (this.nuevaCompra.quantity <= 0) {
      alert('La cantidad debe ser mayor que 0');
      return;
    }
    else if (new Date(this.nuevaCompra.expected_delivery_date) <= this.currentDay) {
      alert('La fecha de entrega debe ser posterior al día actual');
      return;
    }
  
    const orderToSubmit = new PurchaseOrder({
      ...this.nuevaCompra,
      issue_date: this.currentDay.toISOString().split('T')[0],
      expected_delivery_date: this.nuevaCompra.expected_delivery_date
    });
    
    console.log('Submitting order:', orderToSubmit);
  
    this.http.crearOrdenCompra(orderToSubmit, (creada) => {
      console.log('Order created:', creada);
      this.ordenesCompra.push(creada);
      this.nuevaCompra = new PurchaseOrder({
        supplier_id: 0,
        product_id: 0,
        quantity: 0,
        issue_date: this.currentDay,
        expected_delivery_date: new Date(this.currentDay.getTime() + 24*60*60*1000),
        status: 'pending'
      });
      alert('Orden de compra creada correctamente');
    });
  }
}