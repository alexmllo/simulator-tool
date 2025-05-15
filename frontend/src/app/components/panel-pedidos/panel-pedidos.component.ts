import { Component } from '@angular/core';
import {ProductionOrder} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-pedidos',
  standalone:false,
  templateUrl: './panel-pedidos.component.html',
  styleUrl: './panel-pedidos.component.css'
})
export class PanelPedidosComponent {
  pedidosProduccion: ProductionOrder[] = [];

  constructor(private http: HttpService) {
    this.http.getPedidosProduccion((pedidos: ProductionOrder[]) => {
      this.pedidosProduccion = pedidos;
    });
  }
}
