import { Component } from '@angular/core';
import {HttpService} from '../../services/httpService';
import {Product, PurchaseOrder} from '../../classes/models';

@Component({
  selector: 'app-panel-compras',
  standalone:false,
  templateUrl: './panel-compras.component.html',
  styleUrl: './panel-compras.component.css'
})
export class PanelComprasComponent {

  ordenesCompra: PurchaseOrder[] = [];
  productosRaw: Product[] = [];

  constructor(private http: HttpService) {
    this.http.getOrdenesCompra((ordenes: PurchaseOrder[]) => {
      this.ordenesCompra = ordenes;
    });

    this.http.getProductos((productos) => {
      this.productosRaw = productos.filter(p => p.type === 'raw');
    });
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
    this.http.crearOrdenCompra(this.nuevaCompra, (creada) => {
      creada.supplier_id = 0;
      this.ordenesCompra.push(creada);
      this.nuevaCompra = new PurchaseOrder({
        supplier_id: 0,
        product_id: 0,
        quantity: 0,
        issue_date: new Date(),
        expected_delivery_date: new Date(),
        status: 'pending'
      });
    });
  }


}
