# 📦 Simulador de Producción – README

Esta aplicación está compuesta por un backend en Python (FastAPI) y un frontend en Angular.

---

## 🔧 Requisitos

- Python 3.10 o superior  
- Node.js 18 o superior  
- npm  
- Angular CLI (puedes instalarlo con "npm install -g @angular/cli")

---

## 🚀 Backend (Python + FastAPI)

1. Navega a la carpeta del backend:  
   "cd app"

2. Instala las dependencias:  
   "pip install -r requirements.txt"

3. Ejecuta el fichero app.py

El backend estará disponible en: [http://localhost:8000](http://localhost:8000)

---

## 💻 Frontend (Angular)

1. Navega a la carpeta del frontend:  
   "cd frontend"

2. Instala las dependencias:  
   "npm install"

3. Inicia el servidor de desarrollo de Angular:  
   "ng serve"

La aplicación se abrirá en: [http://localhost:4200](http://localhost:4200)

---

## ✅ Notas

- Asegúrate de que el **backend esté en ejecución** antes de usar el frontend.
- El frontend está configurado para comunicarse con el backend en "http://localhost:8000". Si cambias el puerto o el host, actualiza también la variable "serverUrl" en el servicio Angular.
