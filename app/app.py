from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import endpoints
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from db_init import init_db
import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Supply Chain Simulator API",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Initialize database and import initial data
init_db()

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

# Determine frontend path based on environment
def get_frontend_path():
    # First check if we're in a container
    container_path = Path("/app/frontend")
    if container_path.exists():
        return container_path
    
    # If not in container, look for frontend in the project root
    project_root = Path(__file__).resolve().parent.parent
    frontend_path = project_root / "frontend"
    
    # If frontend/dist exists, use that (for production build)
    if (frontend_path / "dist").exists():
        return frontend_path / "dist"
    
    # Otherwise use the frontend directory (for development)
    return frontend_path

frontend_path = get_frontend_path()
print(f"Using frontend path: {frontend_path}")  # Debug print

# Servir archivos estáticos
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
else:
    print(f"Warning: Frontend directory not found at {frontend_path}")

# Página principal
@app.get("/", response_class=HTMLResponse)
def serve_index():
    # Try to find index.html in different possible locations
    possible_locations = [
        frontend_path / "index.html",
        frontend_path / "dist" / "index.html",
        frontend_path / "src" / "index.html"
    ]
    
    for index_file in possible_locations:
        if index_file.exists():
            return FileResponse(index_file)
    
    return HTMLResponse("<h1>index.html no encontrado</h1>", status_code=404)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Supply Chain Simulator API - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
