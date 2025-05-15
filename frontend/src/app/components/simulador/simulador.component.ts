import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../services/httpService';
import {ProductionEvent} from '../../classes/models';

@Component({
  selector: 'app-simulador',
  standalone: false,
  templateUrl: './simulador.component.html',
  styleUrls: ['./simulador.component.css']
})
export class SimuladorComponent implements OnInit {
  diaActual: number | null = null;
  eventos: ProductionEvent[] = [];
  eventosHistoricos: ProductionEvent[] = [];

  constructor(private http: HttpService) {}

  ngOnInit(): void {
    this.cargarEventosHistoricos();
  }

  avanzarDia() {
    this.http.avanzarSimulacion((response) => {
      this.diaActual = response.day;
      this.eventos = response.events;
      this.cargarEventosHistoricos(); // actualizar lista
    });
  }

  cargarEventosHistoricos() {
    this.http.getTodosLosEventos((eventos) => {
      this.eventosHistoricos = eventos;
    });
  }
}
