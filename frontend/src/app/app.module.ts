import {NgModule} from "@angular/core";
import {PanelProduccionComponent} from './components/panel-produccion/panel-produccion.component';
import {PanelComprasComponent} from './components/panel-compras/panel-compras.component';
import {PanelProductosComponent} from './components/panel-productos/panel-productos.component';
import {PanelPedidosComponent} from './components/panel-pedidos/panel-pedidos.component';
import {PanelInventarioComponent} from './components/panel-inventario/panel-inventario.component';
import {HttpService} from './services/httpService';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';

@NgModule({
  declarations: [
    PanelProduccionComponent,
    PanelComprasComponent,
    PanelProductosComponent,
    PanelPedidosComponent,
    PanelInventarioComponent,
  ],
  exports: [
  ],
  imports: [
    CommonModule,
    FormsModule
  ],
  providers:[
    HttpService
  ]
})

export class AppModule {}
