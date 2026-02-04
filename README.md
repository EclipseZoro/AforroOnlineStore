#  Aforro – Backend Developer Assignment (Round-2)

Complete Django + DRF backend showcasing transactional order processing, optimized queries, cached search, Celery workers, and containerized deployment.

## Highlights
- Transactional order workflows with row-level locking
- Search and autocomplete APIs with Redis caching
- Celery background processing for order confirmations
- Optimized listings using select_related, annotations, and pagination
- Dockerized setup for local parity

##  Tech Stack
- Python 3.x
- Django & Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker & Docker Compose

##  Project Structure
```
onlineStore/
 onlineStore/          # settings, URLs, celery bootstrap
 products/
 stores/
 orders/
 search/
 tests/
 Dockerfile
 docker-compose.yml
 requirements.txt
```

##  Setup & Run (Docker)
1. Ensure Docker Desktop is running.
2. Build and start services:
   ```bash
   docker compose up --build
   ```
3. Stash and Apply migrations:
   ```bash
   docker compose exec web python manage.py makemigrations
   docker compose exec web python manage.py migrate
   ```
4. Create a superuser:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
5. Seed sample data:
   ```bash
   docker compose exec web python manage.py seed_data
   ```

Seeding creates 10+ categories, 1000+ products, 20+ stores, and 300+ inventory rows per store.

##  Admin
Visit http://127.0.0.1:8000/admin with the credentials created above.

##  APIs
### 1 Create Order — POST /orders/
```json
{
  "store_id": 1,
  "items": [
    {"product_id": 10, "quantity_requested": 2},
    {"product_id": 12, "quantity_requested": 1}
  ]
}
```
- Insufficient stock on any line item rejects the order.
- Successful orders confirm and deduct stock within a single transaction.

### 2 Store Orders Listing — GET /stores/<store_id>/orders/
- Returns order id, status, created_at, and aggregated quantity.
- Sorted newest first.

### 3 Store Inventory Listing — GET /stores/<store_id>/inventory/
- Returns product title, price, category, and quantity.
- Sorted alphabetically by product title.

### 4 Product Search — GET /api/search/products/
Supported params: q, category, min_price, max_price, store_id, in_stock, sort (price, -price, newest, relevance). When store_id is provided the inventory quantity for that store is included. Responses include pagination metadata.

### 5 Autocomplete — GET /api/search/suggest/?q=...
- Minimum 3 characters, maximum 10 results.
- Prefix matches rank first.
- Returns product titles only.

##  Redis Integration
- Autocomplete endpoint responses are cached under autocomplete:<query> for 10 minutes.
- Significantly reduces repeated DB reads for popular prefixes.

##  Celery Integration
- Redis broker; task send_order_confirmation(order_id) runs after confirmed orders.
- Docker Compose launches the aforro-celery worker automatically.
- On Windows development machines run:
  ```bash
  celery -A onlineStore.celery worker -l info --pool=solo
  ```

##  Tests
Coverage includes confirmed/rejected orders, inventory uniqueness, store listing aggregation, and autocomplete validation.

Run the suite:
```bash
docker compose exec web python manage.py test
```

##  Database Consistency & Transactions
- transaction.atomic() guards order creation.
- select_for_update() locks inventory rows to prevent concurrent double-deduction.

##  Scalability Considerations
- Aggregations and select_related mitigate N+1 queries.
- Redis caching and Celery workers offload read and background workloads.
- PostgreSQL ensures strong transactional guarantees and horizontal scaling is achievable via multiple Django + Celery containers behind a load balancer.

##  Delivered Features
- Strongly typed data models with constraints
- Atomic order processing pipeline
- Optimized store and inventory listings
- Search plus autocomplete with caching
- Celery-based async notifications
- Dockerized local environment
- Automated regression tests
- Assignment completed per specification
