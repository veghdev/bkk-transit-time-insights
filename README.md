# bkk-transit-time-insights

## Overview / Purpose

This demo application collects real-time traffic data from BKK for individual routes.
It calculates average travel times for each route and visualizes variations in travel times
across different days and times of the day on a dashboard.
The application demonstrates a microservice-based architecture, including
data collection, storage, API exposure, and front-end visualization.

## Motivation and Technology Choice

The primary motivation for this demo was curiosity about the variation in travel times across
different days and periods of the day for BKK routes.
The BKK OpenData API provides a free, fair-use API key, which makes it ideal for a demo application
without incurring costs or requiring extensive setup.

### Technology Choices

- **Microservices & Docker Compose:** Chosen to demonstrate a modern, modular architecture where each component (collector, database, API, dashboard) can be developed, tested, and scaled independently.
- **PostgreSQL:** Reliable and widely used relational database, well-suited for storing structured trip data with timestamps
and supporting indexing for efficient queries.
- **Python / APScheduler (collector):** Easy to implement periodic tasks for continuous data collection.
- **FastAPI (API and dashboard):** Lightweight, high-performance Python framework for serving REST endpoints and the simple frontend/dashboard.

## Microservices Overview

### bkk-db

The `bkk-db` service is a PostgreSQL database that stores all collected trip data.

- **Main table:** `trips`, which records each trip's `route_id`, `trip_id`, start and end times, and the timestamp when the data was collected.
- **Indexes:**
  - `idx_trips_route_trip_latest (route_id, trip_id, collected_at DESC)`: Optimizes queries that need the latest trips per route and trip ID, useful for statistics and dashboard updates.
  - `idx_trips_route_id (route_id)`: Speeds up retrieval of distinct route IDs, which is required by the `/routes` API endpoint and other route-level queries.

### bkk-collector

The `bkk-collector` service continuously collects real-time trip updates from the BKK OpenData API (`TripUpdates.pb`) for selected routes. It tracks predicted start and end times for each trip.  

- Collects data for demo routes `0050`, `0070`, and `0090`. The collector can be extended to additional routes if needed.
- Persists trip data every minute using APScheduler.  
- Stores collected data in the `bkk-db` service.  

### api

The `api` service exposes trip data collected in `bkk-db` through REST endpoints. It provides route information and trip statistics for visualization and analysis.

- **Endpoints:**
  - `GET /routes`  
    Returns a list of available route IDs.
  - `GET /find/{route_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`  
    Returns statistics for a specific route over a date range (default: last 7 days). Includes average trip duration and per-day, per-period deviations.

- **Functionality:**
  - Queries `bkk-db` for trip data.
  - Aggregates average travel times by day and time period.
  - Supports optional date filtering for flexible analysis.

### dashboard

The `dashboard` service is a front-end application built with FastAPI, using standard HTML, JavaScript, and CSS to render the interface.
It visualizes trip statistics for selected routes by fetching data from the `api` service and presenting it in an interactive, easy-to-understand format.

- **Route selection:** Users can choose a route from a dropdown menu (dynamically queries the `/find/{route_id}` endpoint of the `api` service).
- **Visualization:** Displays a grouped column chart (using `vizzu-lib`) showing per-day and per-time-period deviations from the average trip duration in minutes.

**Note:** `vizzu-lib` is an open-source visualization library. In this demo, it is loaded via a CDN, so an internet connection is required for proper rendering.

### Supporting Services

- **bkk-db-seed**  
  Populates the `bkk-db` with demo trip data, enabling the application to run without the `bkk-collector` service.
  This is useful for testing the dashboard and API with predefined datasets.

- **bkk-db-pgadmin**  
  Provides a web-based interface (pgAdmin) for inspecting and managing the `bkk-db` database. Useful for debugging, browsing tables, and running manual queries.

## Docker Compose & Deployment / Quick Start

This project uses Docker Compose to orchestrate all microservices. The setup includes multiple profiles for different use cases: data collection, seeding, and database inspection.

### Environment Variables

Set the following environment variables in `.env`. Variables without a default **must** be provided.
Variables with defaults can be overridden if needed.  

- `POSTGRES_USER`: **required**
- `POSTGRES_PASSWORD`: **required**
- `POSTGRES_DB`: **required**
- `POSTGRES_PORT`: **required**
- `POSTGRES_HOST`: `bkk-db` (default)

- `BKK_API_KEY`: **required for bkk-collector service**, obtain from [BKK OpenData portal](https://opendata.bkk.hu/)  
- `BKK_API_URL`: `https://go.bkk.hu/api/query/v1/ws/gtfs-rt/full/TripUpdates.pb` (default)  
- `ROUTE_ID`: `0050,0070,0090` (default)  
- `TZ`: `Europe/Budapest` (default)

- `API_BASE_URL`: `http://api:8000/api/trips` (default)

- `PGADMIN_DEFAULT_EMAIL`: **required for bkk-db-pgadmin service**
- `PGADMIN_DEFAULT_PASSWORD`: **required for bkk-db-pgadmin service**
- `PGADMIN_PORT`: **required for bkk-db-pgadmin service**

### Profiles

Docker Compose profiles allow selective service startup:

- **collect:** Runs the `bkk-collector` service to fetch live data from BKK. Suitable for production or continuous data collection.
- **seed:** Populates the database with demo data using `bkk-db-seed`. Recommended for local testing without relying on the collector.
- **view:** Starts `bkk-db-pgadmin` for database inspection.

### Quick Start

For local testing with demo data:

```bash
docker compose --profile seed up --build
```
This starts the database, API, dashboard, and seeds the database with randomized trip data for the demo routes.
⚠️ Important Note:
The seed job can take some time to complete. To monitor its progress, check the Docker Compose output.

For live data collection (requires a valid BKK_API_KEY):
```bash
docker compose --profile collect up --build
```

Notes:
- All services are connected via the bkk-net network.
- Database data is persisted in the bkk-data volume.
- The dashboard relies on internet access to load vizzu-lib from a CDN for chart rendering.
- **Default Service Ports:**: API: 8000, Dashboard: 3000
