import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  Product,
  InventoryItem,
  PurchaseOrder,
  ProductionOrder, BOMItem, ProductionEvent, DailyPlan
} from '../classes/models';

@Injectable({ providedIn: 'root' })
export class HttpService {
  // Use localhost when running in browser, backend service name when in container
  serverUrl = typeof window !== 'undefined' ? 'http://localhost:8080' : 'http://backend:8080';

  constructor(private http: HttpClient) {
  }

  private handleError(error: any, message: string) {
    console.error(message, error);
    // Only use alert in browser environment
    if (typeof window !== 'undefined') {
      alert(message);
    }
  }

  public getProductos(callback: (productos: Product[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/products/`).subscribe({
      next: (response) => {
        const productos = response.map((p) => new Product(p));
        callback(productos);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de productos')
    });
  }

  public getInventario(callback: (items: InventoryItem[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/inventory/`).subscribe({
      next: (response) => {
        const inventario = response.map((i) => new InventoryItem(i));
        callback(inventario);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de inventario')
    });
  }

  public getOrdenesCompra(callback: (ordenes: PurchaseOrder[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/purchases/orders/`).subscribe({
      next: (response) => {
        const compras = response.map((c) => new PurchaseOrder(c));
        callback(compras);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de compras')
    });
  }

  public getPedidosProduccion(callback: (ordenes: ProductionOrder[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/production/orders/`).subscribe({
      next: (response) => {
        const pedidos = response.map((p) => new ProductionOrder(p));
        callback(pedidos);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de producción')
    });
  }

  public getPedidos(callback: (pedidos: DailyPlan[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/plan/`).subscribe({
      next: (response) => {
        const pedidos = response.map((p) => new DailyPlan(p));
        callback(pedidos);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de pedidos')
    });
  }

  public crearProducto(nuevo: Product, callback: (creado: Product) => void) {
    const payload = {
      id: 0,
      name: nuevo.name,
      type: nuevo.type
    };

    this.http.post(`${this.serverUrl}/app/products`, payload, {
      headers: {'Content-Type': 'application/json'}
    }).subscribe({
      next: (resp: any) => callback(new Product(resp)),
      error: (err) => {
        console.error('Error al crear el producto:', err.error);
        this.handleError(err, 'Error al crear el producto');
      }
    });
  }


  public crearOrdenCompra(nueva: PurchaseOrder, callback: (creada: PurchaseOrder) => void) {
    nueva.id = 0;
    this.http.post(`${this.serverUrl}/app/purchases/orders`, nueva, {
      headers: {'Content-Type': 'application/json'}
    }).subscribe({
      next: (resp: any) => {
        console.log('Server response:', resp);
        callback(new PurchaseOrder(resp));
      },
      error: (error) => {
        console.error('Error creating purchase order:', error);
        this.handleError(error, 'Error al crear la orden de compra: ' + (error.error?.detail || error.message));
      }
    });
  }

  getBOM(productId: number, callback: (items: BOMItem[]) => void) {
    this.http.get<any>(`${this.serverUrl}/app/bom/${productId}`).subscribe({
      next: (res: any[]) => callback(res.map(x => new BOMItem(x))),
      error: () => this.handleError(null, 'Error al cargar la lista de materiales')
    });
  }

  anadirMaterialABOM(productId: number, item: BOMItem, callback: () => void) {
    this.http.post(`${this.serverUrl}/app/bom/${productId}/add`, item).subscribe({
      next: () => callback(),
      error: () => this.handleError(null, 'No se pudo añadir el material')
    });
  }

  eliminarMaterialDeBOM(productId: number, materialId: number, callback: () => void) {
    this.http.delete(`${this.serverUrl}/app/bom/${productId}/remove/${materialId}`).subscribe({
      next: () => callback(),
      error: () => this.handleError(null, 'No se pudo eliminar el material')
    });
  }


  public avanzarSimulacion(callback: (response: any) => void) {
    this.http.post(`${this.serverUrl}/app/simulator/run`, {}).subscribe({
      next: (resp: any) => callback(resp),
      error: () => this.handleError(null, 'Error al avanzar la simulación')
    });
  }

  public getTodosLosEventos(callback: (eventos: ProductionEvent[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/simulator/events/all`).subscribe({
      next: (resp) => callback(resp),
      error: () => this.handleError(null, 'No se pudieron cargar los eventos históricos')
    });
  }

  public iniciarProduccion(orderId: number, callback: () => void) {
    this.http.post(`${this.serverUrl}/app/production/start/${orderId}`, {}).subscribe({
      next: (resp:any) => {
        if(resp.result == "ok"){
          callback()
          alert('Pedido enviado a producción')
        } else {
          alert(resp.result)
        }
      },
      error: () => this.handleError(null, 'No se pudo iniciar la producción')
    });
  }

  public getSuppliers(callback: (providers: any[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/suppliers/`).subscribe({
      next: (response) => {
        callback(response);
      },
      error: () => this.handleError(null, 'No se pudieron obtener los datos de proveedores')
    });
  }

  public getCurrentDay(callback: (response: any) => void) {
    this.http.get<any>(`${this.serverUrl}/app/simulator/current-day`).subscribe({
      next: (response) => {
        callback(response);
      },
      error: () => this.handleError(null, 'No se pudo obtener el día actual de la simulación')
    });
  }

}
