from database import get_session, init_db
from import_service import import_initial_inventory_from_json, import_production_orders_from_json, import_providers_from_json, import_purchase_orders_from_json, import_simulation_from_json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import endpoints
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Supply Chain Simulator API")

# Initialize database and import initial data
init_db()
import_simulation_from_json("data/plan.json")

import_providers_from_json("data/providers.json")
import_initial_inventory_from_json("data/inventory_init.json")
# import_production_orders_from_json("data/production_orders.json")
# import_purchase_orders_from_json("data/purchase_orders.json")


app = FastAPI(title="Simulador Producción 3D")
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # permite solo los orígenes indicados
    allow_credentials=True,
    allow_methods=["*"],     # permite todos los métodos: GET, POST, etc.
    allow_headers=["*"],     # permite todos los headers
)

# Montar rutas de los endpoints
app.include_router(endpoints.router)

# Servir archivos estáticos
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Página principal
@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = frontend_path / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>index.html no encontrado</h1>", status_code=404)
    return FileResponse(index_file)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
