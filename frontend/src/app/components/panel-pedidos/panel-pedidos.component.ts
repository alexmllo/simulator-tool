import { Component } from '@angular/core';
import {Product, DailyPlan, DailyOrder} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-pedidos',
  standalone:false,
  templateUrl: './panel-pedidos.component.html',
  styleUrl: './panel-pedidos.component.css'
})
export class PanelPedidosComponent {
  pedidosProduccion: DailyPlan[] = [];
  productosMap: Map<string, string> = new Map();

  constructor(private http: HttpService) {
    this.http.getPedidos((pedidos: DailyPlan[]) => {
      this.pedidosProduccion = pedidos;
    });

    this.http.getProductos((productos: Product[]) => {
      productos.forEach(p => this.productosMap.set(p.name, p.name));
    });
  }

  getNombreProducto(model: string): string {
    return this.productosMap.get(model) || model;
  }

  mandarAProduccion(pedidoId: number) {
    this.http.iniciarProduccion(pedidoId, () => {
      const pedido = this.pedidosProduccion.find(x => x.id === pedidoId);
      if (pedido) {
        pedido.orders.forEach(order => {
          order.status = 'in_production';
        });
      }
    });
  }
}
