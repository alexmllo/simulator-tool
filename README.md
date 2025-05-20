# Production Simulator

A comprehensive production simulation and management system that helps businesses model, analyze, and optimize their production processes. This tool simulates daily production operations, inventory management, and order fulfillment in a controlled environment.

## Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
  - [Using Docker (Recommended)](#using-docker-recommended)
  - [Manual Setup (Alternative)](#manual-setup-alternative)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
- [Usage](#-usage)
- [Important Notes](#️-important-notes)
- [Contributing](#-contributing)
- [License](#-license)


## Features

- **Daily Production Simulation**: Simulate production processes day by day
- **Inventory Management**: Track and manage raw materials and finished products
- **Order Management**: Handle production orders and purchase orders
- **Real-time Event Tracking**: Monitor production events and system status
- **Interactive Dashboard**: Visualize production metrics and system state
- **Historical Analysis**: Review past production events and performance

## Architecture

The application is built with a modern tech stack:

- **Backend**: Python with FastAPI
- **Frontend**: Angular 19
- **Database**: SQLAlchemy ORM
- **Simulation Engine**: SimPy for discrete event simulation

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd simulator-tool
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8080

### Manual Setup (Alternative)

If you prefer to run the application without Docker:

#### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm
- Angular CLI (`npm install -g @angular/cli`)

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd app
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python app.py
   ```
   The backend will be available at: http://localhost:8000

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   ng serve
   ```
   The application will be available at: http://localhost:4200

## 📊 Usage

1. Access the application through your web browser at http://localhost:4200
2. Use the simulator interface to:
   - View the current simulation day
   - Advance the simulation day by day
   - Monitor production events
   - Track inventory levels
   - Manage production orders
   - View historical data

## ⚠️ Important Notes

- The application uses Docker volumes to persist the database data
- The frontend is configured to communicate with the backend through Docker's internal network
- If you need to change the backend URL, update the `serverUrl` variable in the Angular service

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
