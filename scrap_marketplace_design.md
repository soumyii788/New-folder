# Scrap Marketplace Backend Architecture

This document provides a robust, highly scalable Django-based architecture designed for high-throughput marketplace operations, typical of modern logistics and recycling platforms like ScrapUncle.

## 1. Complete Folder Structure

We organize the backend using a **service-oriented modular structure**. This keeps concerns separated and prevents a massive monolithic spaghetti codebase.

```text
scrap_marketplace/
├── docker-compose.yml
├── Dockerfile
├── gunicorn.conf.py
├── production_deployment_guide.md
├── requirements.txt
├── .env.example
├── nginx/
│   └── nginx.conf
└── backend/                     # Django Root
    ├── manage.py
    ├── common/                  # Shared utilities, base abstract models (e.g., TimeStampedModel), auth mixins
    ├── config/                  # Main Config
    │   ├── asgi.py              # Channels routing for WebSockets
    │   ├── celery.py            # Async background tasks config (Redis broker)
    │   ├── urls.py              # API router mapping
    │   ├── wsgi.py              # Gunicorn entrypoint
    │   └── settings/            # Modular environments
    │       ├── base.py          # Shared definitions
    │       ├── local.py         # Local dev (Debug=True, SQLite/Local PG)
    │       └── production.py    # Prod (Debug=False, AWS RDS, Redis, S3)
    └── apps/                    # Core Business Services
        ├── accounts/            # Users, JWT auth, OTP, Role validations
        ├── catalog/             # Scrap categories, dynamic pricing matrix
        ├── customers/           # User profiles, geo-validated addresses
        ├── notifications/       # SMS, Push, Email Celery workers
        ├── pickups/             # Request lifecycle, geo-assignment logic
        ├── tracking/            # WebSockets: live collector coordinate broadcasting
        └── wallet/              # Payment integrations, transactions
```

## 2. Database Schema Design (PostgreSQL)

* **`accounts_user` (AbstractBaseUser)**
  * `id` (UUID)
  * `phone_number` (String, Unique)
  * `role` (Enum: CUSTOMER, COLLECTOR, ADMIN)
  * `is_verified` (Boolean) - verified via OTP

* **`customers_profile`**
  * `user` (O2O `accounts_user`)
  * `first_name`, `last_name`
  * `avatar` (Image/URL)

* **`customers_address`**
  * `customer` (FK `customers_profile`)
  * `label` (Enum: HOME, OFFICE, OTHER)
  * `lat`, `long` (Decimal / PostGIS Point for spatial queries)
  * `address_line1`, `city`, `state`, `zip_code`

* **`accounts_collector`**
  * `user` (O2O `accounts_user`)
  * `vehicle_type` (Enum: BIKE, TEMPO, TRUCK)
  * `kyc_status` (Enum: PENDING, APPROVED, REJECTED)
  * `is_available` (Boolean)
  * `current_lat`, `current_long` - for assignment distance logic

* **`catalog_scrapcategory`**
  * `id` (UUID)
  * `name` (String, e.g., "Iron", "Newspaper")
  * `base_price_per_kg` (Decimal) - Controllable by admin
  * `icon` (URL)

* **`pickups_pickuprequest`**
  * `id` (UUID)
  * `customer` (FK `customers_profile`)
  * `assigned_collector` (FK `accounts_collector`, Nullable)
  * `status` (Enum: REQUESTED, ASSIGNED, ON_THE_WAY, COMPLETED, CANCELLED)
  * `scheduled_time` (DateTime)
  * `total_payout` (Decimal)

* **`pickups_pickupitem`**
  * `pickup` (FK `pickups_pickuprequest`)
  * `category` (FK `catalog_scrapcategory`)
  * `actual_weight_kg` (Decimal)
  * `calculated_price` (Decimal)

* **`wallet_transaction`**
  * `id` (UUID)
  * `user` (FK `accounts_user`)
  * `amount` (Decimal)
  * `txn_type` (Enum: CREDIT, DEBIT)
  * `status` (Enum: PENDING, SUCCESS, FAILED)

## 3. API Endpoints List

API follows REST best practices, returning standard JSON schemas.

### Authentication (`/api/v1/auth`)
* `POST /send-otp/` - Request a one-time password via SMS.
* `POST /verify-otp/` - Exchanges OTP for short-lived JWT.

### Customer Operations (`/api/v1/customers`)
* `GET/PUT /profile/` - Manage customer details.
* `GET/POST /addresses/` - Address book for pickup locations.

### Scrap Pricing (`/api/v1/catalog`)
* `GET /categories/` - Sync latest prices to mobile app.

### Pickup Management (`/api/v1/pickups`)
* `POST /request/` - Schedule a scrap collection job.
* `GET /history/` - View previous interactions.

### Collector Ops (`/api/v1/collectors`)
* `GET /jobs/nearby/` - Query returning unassigned pickups.
* `POST /jobs/:id/accept/` - Lock a pickup.
* `PATCH /jobs/:id/status/` - Collector workflow progress.
* `POST /location/` - Frequent polling endpoint to send GNSS coordinates.

### Wallet (`/api/v1/wallet`)
* `GET /balance/` - Total earnings.
* `GET /transactions/` - Payouts and charges ledger.

## 4. Setup Instructions

1. **Docker Setup:** Run `docker-compose up --build -d`
2. **Migrations:** `docker-compose exec web python backend/manage.py migrate`

## 5. Sample Core Workflow

1. **Catalog Sync**: UI calls `GET /catalog/categories/`
2. **Init Pickup**: Customer hits `POST /request/`. 
3. **Queue Broadcast**: Backend sets status to `REQUESTED`.
4. **Collector Claim**: A collector sees the job on `GET /jobs/nearby/` and hits `POST /accept/`.
5. **En-Route Tracking**: Status becomes `ON_THE_WAY`. Collector constantly pulses `POST /location/`.
6. **Settlement**: Server computes the final sum via `wallet` module.
7. **Completion**: Pick status hits `COMPLETED`. Both get confirmation.
