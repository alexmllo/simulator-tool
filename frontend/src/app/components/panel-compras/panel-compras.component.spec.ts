import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PanelComprasComponent } from './panel-compras.component';

describe('PanelComprasComponent', () => {
  let component: PanelComprasComponent;
  let fixture: ComponentFixture<PanelComprasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelComprasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PanelComprasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
