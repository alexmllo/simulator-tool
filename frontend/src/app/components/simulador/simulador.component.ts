import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../services/httpService';
import { ProductionEvent } from '../../classes/models';

@Component({
  selector: 'app-simulador',
  standalone: false,
  templateUrl: './simulador.component.html',
  styleUrls: ['./simulador.component.css']
})
export class SimuladorComponent implements OnInit {
  diaActual: Date | null = null;
  eventos: ProductionEvent[] = [];
  eventosHistoricos: ProductionEvent[] = [];

  constructor(private http: HttpService) {}

  ngOnInit(): void {
    this.cargarEventosHistoricos();
  }

  avanzarDia() {
    this.http.avanzarSimulacion((response) => {
      this.diaActual = new Date(response.day);
      this.eventos = response.events.map((event: any) => new ProductionEvent(event));
      this.cargarEventosHistoricos(); // actualizar lista
    });
  }

  cargarEventosHistoricos() {
    this.http.getTodosLosEventos((eventos) => {
      this.eventosHistoricos = eventos.map((event: any) => new ProductionEvent(event));
    });
  }

  get formattedCurrentDay(): string {
    if (!this.diaActual) return '';
    const day = this.diaActual.getDate().toString().padStart(2, '0');
    const month = (this.diaActual.getMonth() + 1).toString().padStart(2, '0');
    const year = this.diaActual.getFullYear();
    return `${day}/${month}/${year}`;
  }
}
