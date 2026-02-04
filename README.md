🛒 Aforro – Backend Developer Assignment (Round-2)

This project implements a complete backend module using Django + Django REST Framework, demonstrating:

transactional order processing

query optimization

search and autocomplete APIs

Redis caching

Celery asynchronous tasks

Dockerized deployment

🧱 Tech Stack

Python

Django & Django REST Framework

PostgreSQL

Redis

Celery

Docker & Docker Compose

📁 Project Structure
onlineStore/
├── onlineStore/          # main project (settings, urls, celery)
├── products/
├── stores/
├── orders/
├── search/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

⚙️ Setup & Run (Docker)

Make sure Docker Desktop is running.

From the project root:

docker compose up --build

Run migrations
docker compose exec web python manage.py migrate

Create admin user
docker compose exec web python manage.py createsuperuser

Seed dummy data
docker compose exec web python manage.py seed_data


This generates:

10+ categories

1000+ products

20+ stores

at least 300 inventory items per store

🔐 Admin
http://127.0.0.1:8000/admin

📌 APIs
1️⃣ Create Order
POST /orders/


Example:

{
  "store_id": 1,
  "items": [
    {"product_id": 10, "quantity_requested": 2},
    {"product_id": 12, "quantity_requested": 1}
  ]
}


Behaviour

If any product has insufficient stock → order is REJECTED

If all are available → order is CONFIRMED and stock is deducted

The operation is fully wrapped inside a database transaction

2️⃣ Store Orders Listing
GET /stores/<store_id>/orders/


Returns:

order id

status

created_at

total number of items (sum of quantities)

Sorted by newest first.

3️⃣ Store Inventory Listing
GET /stores/<store_id>/inventory/


Returns:

product title

price

category name

quantity

Sorted alphabetically by product title.

4️⃣ Product Search
GET /api/search/products/


Supported parameters:

q

category

min_price

max_price

store_id

in_stock

sort ( price, -price, newest, relevance )

If store_id is provided, inventory quantity for that store is included.

Pagination metadata is included.

5️⃣ Autocomplete
GET /api/search/suggest/?q=xxx


Rules:

minimum 3 characters

maximum 10 results

prefix matches appear first

only product titles are returned

🧠 Redis Integration

Redis is used as a cache for the autocomplete API.

Cached endpoint:

GET /api/search/suggest/


Cache key format:

autocomplete:<query>


A TTL-based strategy (5 minutes) is used for invalidation.

This significantly reduces repeated database hits for frequently searched prefixes.

🔁 Celery Integration

Celery is configured with Redis as the message broker.

An asynchronous task is triggered when an order is successfully confirmed.

Example task:

send_order_confirmation(order_id)

The task simulates background processing such as sending an order confirmation.

Running Celery (Docker)

Celery worker is started automatically using Docker Compose:

aforro-celery

Local development (Windows)

For local development on Windows, Celery is started using the solo pool:

celery -A onlineStore.celery worker -l info --pool=solo


This is required due to multiprocessing limitations on Windows.

🧪 Tests

The project contains 5 automated tests that cover:

confirmed order creation and stock deduction

rejected order when stock is insufficient

inventory uniqueness constraint

store order listing aggregation

autocomplete minimum character rule

Run tests:

docker compose exec web python manage.py test

🧩 Database Consistency & Transactions

Order creation is wrapped inside:

transaction.atomic()


Inventory rows are locked using:

select_for_update()


This prevents race conditions and double-deduction when multiple orders are created concurrently.

🚀 Scalability Considerations

Inventory and order listing queries use aggregation and select_related to avoid N+1 queries.

Autocomplete responses are cached using Redis to reduce read load.

Asynchronous processing using Celery keeps API response times low.

PostgreSQL is used to provide strong transactional guarantees.

The architecture allows horizontal scaling of Django and Celery workers behind a load balancer.

✅ Features Completed

Data models with proper constraints

Atomic order processing

Optimized listing APIs

Product search and autocomplete

Redis caching

Celery background tasks

Dockerized environment

Automated test coverage

Assignment completed as per the provided specification.