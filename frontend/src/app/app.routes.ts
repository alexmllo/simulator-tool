import { Routes } from '@angular/router';
import {MainComponentComponent} from './main-component/main-component.component';
import {PanelComprasComponent} from './components/panel-compras/panel-compras.component';
import {PanelInventarioComponent} from './components/panel-inventario/panel-inventario.component';
import {PanelPedidosComponent} from './components/panel-pedidos/panel-pedidos.component';
import {PanelProduccionComponent} from './components/panel-produccion/panel-produccion.component';
import {PanelProductosComponent} from './components/panel-productos/panel-productos.component';

export const routes: Routes = [
  {path:'', component:MainComponentComponent,
  children: [
     {path:'compras', component: PanelComprasComponent},
     {path:'inventario', component: PanelInventarioComponent},
     {path:'pedidos', component: PanelPedidosComponent},
     {path:'produccion', component: PanelProduccionComponent},
     {path:'productos', component: PanelProductosComponent},
  ]},
];
