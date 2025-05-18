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
  eventosAgrupados: { [key: string]: ProductionEvent[] } = {};

  constructor(private http: HttpService) {}

  ngOnInit(): void {
    this.cargarDiaActual();
    this.cargarEventosHistoricos();
  }

  cargarDiaActual() {
    this.http.getCurrentDay((response) => {
      const currentDate = new Date(response.day);
      if (!isNaN(currentDate.getTime())) {
        currentDate.setDate(currentDate.getDate() + 1);
        this.diaActual = currentDate;
        this.cargarEventosDelDia();
      } else {
        this.diaActual = null;
      }
    });
  }

  cargarEventosDelDia() {
    if (!this.diaActual) {
      this.eventos = [];
      return;
    }
    const formatted = this.formattedCurrentDay;
    this.eventos = this.eventosHistoricos.filter(
      (evento) => evento.formattedDate === formatted
    );
  }

  avanzarDia() {
    this.http.avanzarSimulacion((response) => {
      this.diaActual = new Date(response.day);
      this.eventos = response.events.map((event: any) => new ProductionEvent(event));
      this.cargarEventosHistoricos();
    });
  }

  cargarEventosHistoricos() {
    this.http.getTodosLosEventos((eventos) => {
      this.eventosHistoricos = eventos.map((event: any) => new ProductionEvent(event));
      this.agruparEventosPorDia();
      this.cargarEventosDelDia();
    });
  }

  agruparEventosPorDia() {
    this.eventosAgrupados = {};
    this.eventosHistoricos.forEach(evento => {
      const fecha = evento.formattedDate;
      if (!this.eventosAgrupados[fecha]) {
        this.eventosAgrupados[fecha] = [];
      }
      this.eventosAgrupados[fecha].push(evento);
    });
  }

  get formattedCurrentDay(): string {
    if (!this.diaActual || isNaN(this.diaActual.getTime())) return '';
    const day = this.diaActual.getDate().toString().padStart(2, '0');
    const month = (this.diaActual.getMonth() + 1).toString().padStart(2, '0');
    const year = this.diaActual.getFullYear();
    return `${day}/${month}/${year}`;
  }
}
