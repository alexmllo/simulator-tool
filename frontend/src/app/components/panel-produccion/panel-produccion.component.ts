import { Component } from '@angular/core';
import {ProductionOrder} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-produccion',
  standalone:false,
  templateUrl: './panel-produccion.component.html',
  styleUrl: './panel-produccion.component.css'
})
export class PanelProduccionComponent {
  ordenesProduccion: ProductionOrder[] = [];

  constructor(private http: HttpService) {
    this.http.getPedidosProduccion((ordenes: ProductionOrder[]) => {
      this.ordenesProduccion = ordenes;
    });
  }
}
