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
  serverUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) {
  }

  public getProductos(callback: (productos: Product[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/products/`).subscribe({
      next: (response) => {
        const productos = response.map((p) => new Product(p));
        callback(productos);
      },
      error: () => alert('No se pudieron obtener los datos de productos')
    });
  }

  public getInventario(callback: (items: InventoryItem[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/inventory/`).subscribe({
      next: (response) => {
        const inventario = response.map((i) => new InventoryItem(i));
        callback(inventario);
      },
      error: () => alert('No se pudieron obtener los datos de inventario')
    });
  }

  public getOrdenesCompra(callback: (ordenes: PurchaseOrder[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/purchases/orders/`).subscribe({
      next: (response) => {
        const compras = response.map((c) => new PurchaseOrder(c));
        callback(compras);
      },
      error: () => {
        alert('No se pudieron obtener los datos de compras')
      }
    });
  }

  public getPedidosProduccion(callback: (ordenes: ProductionOrder[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/production/orders/`).subscribe({
      next: (response) => {
        const pedidos = response.map((p) => new ProductionOrder(p));
        callback(pedidos);
      },
      error: () => alert('No se pudieron obtener los datos de producción')
    });
  }

  public getPedidos(callback: (pedidos: DailyPlan[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/plan/`).subscribe({
      next: (response) => {
        const pedidos = response.map((p) => new DailyPlan(p));
        callback(pedidos);
      },
      error: () => alert('No se pudieron obtener los datos de pedidos')
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
        alert('Error al crear el producto');
      }
    });
  }


  public crearOrdenCompra(nueva: PurchaseOrder, callback: (creada: PurchaseOrder) => void) {
    nueva.id = 0
    this.http.post(`${this.serverUrl}/app/purchases/orders`, nueva).subscribe({
      next: (resp: any) => callback(new PurchaseOrder(resp)),
      error: () => alert('Error al crear la orden de compra')
    });
  }

  getBOM(productId: number, callback: (items: BOMItem[]) => void) {
    this.http.get<any>(`${this.serverUrl}/app/bom/${productId}`).subscribe({
      next: (res: any[]) => callback(res.map(x => new BOMItem(x))),
      error: () => alert('Error al cargar la lista de materiales')
    });
  }

  anadirMaterialABOM(productId: number, item: BOMItem, callback: () => void) {
    this.http.post(`${this.serverUrl}/app/bom/${productId}/add`, item).subscribe({
      next: () => callback(),
      error: () => alert('No se pudo añadir el material')
    });
  }

  eliminarMaterialDeBOM(productId: number, materialId: number, callback: () => void) {
    this.http.delete(`${this.serverUrl}/app/bom/${productId}/remove/${materialId}`).subscribe({
      next: () => callback(),
      error: () => alert('No se pudo eliminar el material')
    });
  }


  public avanzarSimulacion(callback: (response: any) => void) {
    this.http.post(`${this.serverUrl}/app/simulator/run`, {}).subscribe({
      next: (resp: any) => callback(resp),
      error: () => alert('Error al avanzar la simulación')
    });
  }

  public getTodosLosEventos(callback: (eventos: ProductionEvent[]) => void) {
    this.http.get<any[]>(`${this.serverUrl}/app/simulator/events/all`).subscribe({
      next: (resp) => callback(resp),
      error: () => alert('No se pudieron cargar los eventos históricos')
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
      error: () => alert('No se pudo iniciar la producción')
    });
  }


}
