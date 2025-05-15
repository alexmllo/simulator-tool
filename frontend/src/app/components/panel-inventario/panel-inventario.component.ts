import { Component } from '@angular/core';
import {InventoryItem} from '../../classes/models';
import {HttpService} from '../../services/httpService';

@Component({
  selector: 'app-panel-inventario',
  standalone:false,
  templateUrl: './panel-inventario.component.html',
  styleUrl: './panel-inventario.component.css'
})
export class PanelInventarioComponent {

   inventario: InventoryItem[] = [];

  constructor(private http: HttpService) {
    this.http.getInventario((items: InventoryItem[]) => {
      this.inventario = items;
    });
  }

}
