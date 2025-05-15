import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PanelProduccionComponent } from './panel-produccion.component';

describe('PanelProduccionComponent', () => {
  let component: PanelProduccionComponent;
  let fixture: ComponentFixture<PanelProduccionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelProduccionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PanelProduccionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
