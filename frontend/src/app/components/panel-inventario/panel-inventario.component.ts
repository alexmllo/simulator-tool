import { Component } from '@angular/core';
import {InventoryItem, Product} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-inventario',
  standalone:false,
  templateUrl: './panel-inventario.component.html',
  styleUrl: './panel-inventario.component.css'
})
export class PanelInventarioComponent {

   inventario: InventoryItem[] = [];
  productosMap: Map<number, string> = new Map();

  constructor(private http: HttpService) {
    this.http.getInventario((items: InventoryItem[]) => {
      this.inventario = items;
    });

    this.http.getProductos((productos: Product[]) => {
      productos.forEach(p => this.productosMap.set(p.id, p.name));
    });
  }

    getNombreProducto(id: number): string {
    return this.productosMap.get(id) || `#${id}`;
  }
}
