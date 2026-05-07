# Scrap Recycling Marketplace

Welcome to the Scrap Recycling Marketplace project! This is a robust, highly scalable backend system designed for high-throughput marketplace operations, tailored for modern scrap collection, recycling, and logistics platforms.

## Overview

The platform connects **Customers** who want to sell scrap with **Collectors** who pick up the scrap, managed by an **Admin** dashboard. It features real-time tracking, dynamic pricing, digital wallet transactions, and automated logistics workflows.

## Technology Stack

* **Backend Framework:** Python / Django
* **Database:** PostgreSQL (with PostGIS for spatial queries)
* **Caching & Message Broker:** Redis
* **Background Tasks:** Celery
* **Real-time Communication:** Django Channels (WebSockets)
* **Deployment & Containerization:** Docker, Docker Compose, Nginx, Gunicorn

## Project Structure

This project uses a service-oriented modular architecture to keep concerns separated and maintain a clean codebase.

```text
scrap_marketplace/
├── backend/                     # Django Root
│   ├── apps/                    # Core Business Services (accounts, catalog, pickups, etc.)
│   ├── config/                  # Main Configurations (settings, urls, asgi, wsgi, celery)
│   └── common/                  # Shared utilities and base abstract models
├── nginx/                       # Nginx configuration
├── docker-compose.yml           # Docker Compose services definition
├── Dockerfile                   # Docker image configuration for the web service
├── gunicorn.conf.py             # Gunicorn WSGI server configuration
└── requirements.txt             # Python dependencies
```

## Setup & Installation

This project is fully containerized with Docker, making local setup simple and straightforward.

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Running Locally

1. **Clone the repository** and navigate to the project directory.

2. **Environment Variables:**
   Copy the example environment file and update the variables if necessary.
   ```bash
   cp .env.example .env
   ```

3. **Build and start the containers:**
   ```bash
   docker-compose up --build -d
   ```

4. **Run Database Migrations:**
   ```bash
   docker-compose exec web python backend/manage.py migrate
   ```

5. **Create a Superuser (Optional):**
   ```bash
   docker-compose exec web python backend/manage.py createsuperuser
   ```

The application will now be running and accessible via `http://localhost` (or whatever port Nginx is mapped to).

## Core Features & Workflows

1. **Role-Based Access Control:** Secure JWT authentication with OTP verification for Customers, Collectors, and Admins.
2. **Dynamic Scrap Catalog:** Centralized pricing matrix controlled by admins, syncing live with mobile/web clients.
3. **Smart Pickup Assignment:** Geolocation-based routing using PostGIS to assign nearby available collectors.
4. **Real-time Tracking:** Continuous collector coordinate broadcasting to customers via WebSockets.
5. **Digital Wallet:** Integrated transaction ledger for tracking customer payouts and collector earnings.

## API Documentation

The REST API endpoints follow standard conventions. Here's a brief overview:

* **Auth:** `/api/v1/auth/` (OTP request, verification)
* **Customers:** `/api/v1/customers/` (Profiles, addresses)
* **Catalog:** `/api/v1/catalog/` (Scrap categories and prices)
* **Pickups:** `/api/v1/pickups/` (Requests, history)
* **Collectors:** `/api/v1/collectors/` (Nearby jobs, accept jobs, location polling)
* **Wallet:** `/api/v1/wallet/` (Balances, transactions)

## Deployment

For production deployments, please refer to the detailed `production_deployment_guide.md` included in the root directory.

## Documentation

* [Architecture & Design Details](scrap_marketplace_design.md)
* [Production Deployment Guide](production_deployment_guide.md)
