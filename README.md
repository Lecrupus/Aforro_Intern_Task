# High-Performance E-Commerce Backend 

A scalable, production-ready backend built using **Django 5** and **Django Rest Framework (DRF)**.

This project demonstrates how to build high-concurrency e-commerce systems, focusing on **atomic inventory management** (preventing race conditions), **high-performance search** with Redis caching and throttling, and **asynchronous task execution** using Celery.

---

## Tech Stack

- **Framework:** Django 5, Django Rest Framework
- **Database:** PostgreSQL
- **Cache & Message Broker:** Redis
- **Asynchronous Processing:** Celery
- **Containerization:** Docker, Docker Compose

---

## Quick Start

### 1. Run the Project
Start all services (Django app, PostgreSQL, Redis, Celery worker) with a single command:

```bash
docker compose up --build

### 2. Seed Test Data
Populate the database with sample stores, products, and inventory:

```bash
docker compose exec web python manage.py seed_data

## Features & API Documentation

### Feature 1: Advanced Product Search
A high-performance search API with dynamic filtering and store-specific inventory annotation.

**Endpoint:** `GET /api/search/products/`

| Feature | Method | Endpoint Example |
| :--- | :--- | :--- |
| **Basic Search** | `GET` | `/api/search/products/?q=Pro` |
| **Filter by Price** | `GET` | `/api/search/products/?min_price=10&max_price=100` |
| **Filter by Category** | `GET` | `/api/search/products/?category=Electronics` |
| **Check Store Stock** | `GET` | `/api/search/products/?q=Pro&store_id=1` |
| **In-Stock Only** | `GET` | `/api/search/products/?store_id=1&in_stock=true` |

> **Note:** The `store_quantity` field is returned only when `store_id` is provided in the query parameters.

### Feature 2: Autocomplete Search (Rate Limited)
Prefix-based autocomplete suggestions with **Redis-backed throttling** to prevent abuse.

**Endpoint:** `GET /api/search/suggest/`

**Rules:**
* Minimum **3 characters** required.
* Prefix matches are prioritized.
* **Rate Limit:** 20 requests per minute per user.
* Exceeding the limit returns `HTTP 429 Too Many Requests`.

**Example:**
```http
GET /api/search/suggest/?q=Pro

### Feature 3: Atomic Order Processing
Handles high-concurrency ordering using `transaction.atomic()` and `select_for_update()`. This locks the relevant rows during the transaction, preventing race conditions (e.g., preventing the same item from being sold to two different users simultaneously).



**Endpoint:** `POST /orders/`

#### Successful Order Example

**Curl (macOS/Linux):**
```bash
curl -X POST http://localhost:8000/orders/ \
-H "Content-Type: application/json" \
-d '{"store": 1, "items": [{"product_id": 589, "quantity": 1}]}'

**PowerShell (Windows):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/orders/" -Method Post `
-ContentType "application/json" `
-Body '{"store": 1, "items": [{"product_id": 589, "quantity": 1}]}'

**Result:** Order status `CONFIRMED`, inventory deducted.

#### Insufficient Stock Example
Payload requesting more items than available:

```json
{
  "store": 1,
  "items": [
    {
      "product_id": 589,
      "quantity": 1000000
    }
  ]
}

**Result:** Order status `REJECTED`, inventory remains unchanged.

---

### Feature 4: Store Inventory and Orders

**View Orders**
Sorted newest to oldest.
```http
GET /stores/1/orders/

**View Inventory**
Sorted alphabetically by product title.
```http
GET /stores/1/inventory/

### Feature 5: Asynchronous Tasks with Celery
Heavy operations, such as sending order confirmation emails, are handled asynchronously to ensure fast API response times.



**Verification Steps:**

1. Open a terminal and tail the worker logs:
   ```bash
   docker compose logs -f worker
2. Place a successful order via the API.
3. The API will respond instantly with `HTTP 201`.
4. The worker logs will show the email task being processed and sent after a short delay.

---

## Running Tests

Run the automated test suite inside the Docker container:

```bash
docker compose exec web python manage.py test