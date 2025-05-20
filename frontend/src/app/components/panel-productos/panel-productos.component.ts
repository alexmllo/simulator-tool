import { Component } from '@angular/core';
import {HttpService} from '../../services/httpService';
import {BOMItem, Product} from '../../classes/models';

@Component({
  selector: 'app-panel-productos',
  standalone:false,
  templateUrl: './panel-productos.component.html',
  styleUrl: './panel-productos.component.css'
})
export class PanelProductosComponent {

   materiasPrimas: Product[] = [];
  productosFinales: Product[] = [];
  bom: { [productId: number]: BOMItem[] } = {};
  nuevoMaterial: { [productId: number]: BOMItem } = {};

  nuevaMateriaPrima = new Product({ name: '', type: 'raw' });
  nuevoProductoFinal = new Product({ name: '', type: 'finished' });

  constructor(private http: HttpService) {
    this.cargarProductos();
  }

  cargarProductos() {
    this.http.getProductos((productos) => {
      this.materiasPrimas = productos.filter(p => p.type === 'raw');
      this.productosFinales = productos.filter(p => p.type === 'finished');

      // Cargar la BOM para cada producto final
      for (let pf of this.productosFinales) {
        // @ts-ignore
        this.http.getBOM(pf.id, (componentes) => {
        // @ts-ignore
          this.bom[pf.id] = componentes;
        // @ts-ignore
          this.nuevoMaterial[pf.id] = new BOMItem({ material_id: 0, quantity: 1 });
        });
      }
    });
  }

  crearMateriaPrima() {
    this.nuevaMateriaPrima.type = 'raw';
    this.http.crearProducto(this.nuevaMateriaPrima, (creado) => {
      this.cargarProductos();
    });
  }

  crearProductoFinal() {
    this.nuevoProductoFinal.type = 'finished';
    this.http.crearProducto(this.nuevoProductoFinal, (creado) => {
      alert('Producto creado. Por favor, añada al menos un material a la lista de materiales (BOM) para poder producirlo.');
      this.cargarProductos();
    });
  }

  anadirMaterial(productId: number) {
    const mat = this.nuevoMaterial[productId];
    this.http.anadirMaterialABOM(productId, mat, () => {
     this.cargarProductos();
    });
  }

  quitarMaterial(productId: number, materialId: number) {
    this.http.eliminarMaterialDeBOM(productId, materialId, () => {
     this.cargarProductos();
    });
  }

  getNombreMateriaPrima(id: number): string {
    return this.materiasPrimas.find(mp => mp.id === id)?.name || '(desconocido)';
  }

}
