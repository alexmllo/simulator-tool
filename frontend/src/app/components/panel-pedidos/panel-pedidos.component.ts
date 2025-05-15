import { Component } from '@angular/core';
import {Product, ProductionOrder} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-pedidos',
  standalone:false,
  templateUrl: './panel-pedidos.component.html',
  styleUrl: './panel-pedidos.component.css'
})
export class PanelPedidosComponent {
  pedidosProduccion: ProductionOrder[] = [];
  productosMap: Map<number, string> = new Map();

  constructor(private http: HttpService) {
    this.http.getPedidosProduccion((pedidos: ProductionOrder[]) => {
      this.pedidosProduccion = pedidos;
    });


    this.http.getProductos((productos: Product[]) => {
      productos.forEach(p => this.productosMap.set(p.id, p.name));
    });
  }

   getNombreProducto(id: number): string {
    return this.productosMap.get(id) || `#${id}`;
  }
}
