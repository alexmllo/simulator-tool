import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {AppModule} from './app.module';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, AppModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'simulator-frontend';
}
