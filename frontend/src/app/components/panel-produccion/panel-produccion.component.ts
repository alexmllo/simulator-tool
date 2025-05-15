import { Component } from '@angular/core';
import {Product, ProductionOrder} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-produccion',
  standalone:false,
  templateUrl: './panel-produccion.component.html',
  styleUrl: './panel-produccion.component.css'
})
export class PanelProduccionComponent {
  ordenesProduccion: ProductionOrder[] = [];
  productosMap: Map<number, string> = new Map();

  constructor(private http: HttpService) {
    this.http.getPedidosProduccion((ordenes: ProductionOrder[]) => {
      this.ordenesProduccion = ordenes;
    });

    this.http.getProductos((productos: Product[]) => {
      productos.forEach(p => this.productosMap.set(p.id, p.name));
    });
  }


   getNombreProducto(id: number): string {
    return this.productosMap.get(id) || `#${id}`;
  }
}
