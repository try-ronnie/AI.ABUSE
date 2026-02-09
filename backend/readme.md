# Farmart Backend

FastAPI-based backend for the Farmart e-commerce application.

## Quick Start

### 1. Create virtual environment and install dependencies

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r .requirements.txt
```

### 2. Initialize the database

```bash
./venv/bin/python seed_data.py
```

This will create the SQLite database and seed it with test users and animals.

### 3. Run the server

```bash
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

### 4. Access the API documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Test Accounts

After running `seed_data.py`, the following test accounts are available:

| Role | Email | Password |
|------|-------|----------|
| Farmer | farmer@test.com | password123 |
| Farmer 2 | farmer2@test.com | password123 |
| Buyer | buyer@test.com | password123 |
| Buyer 2 | buyer2@test.com | password123 |

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/farmer` - Get farmer profile
- `PATCH /api/v1/users/me/farmer` - Update farmer profile

### Animals
- `GET /api/v1/animals/` - List animals (with filtering)
- `GET /api/v1/animals/{id}` - Get animal details
- `POST /api/v1/animals/` - Create animal (farmer only)
- `PATCH /api/v1/animals/{id}` - Update animal (farmer only)
- `DELETE /api/v1/animals/{id}` - Delete animal (farmer only)
- `GET /api/v1/animals/farmer/my-animals` - Get farmer's animals

### Cart
- `GET /api/v1/cart/` - List cart items
- `POST /api/v1/cart/` - Add item to cart
- `PATCH /api/v1/cart/{id}` - Update cart item
- `DELETE /api/v1/cart/{id}` - Remove item from cart
- `DELETE /api/v1/cart/` - Clear cart

### Orders
- `POST /api/v1/orders/checkout` - Create order from cart
- `GET /api/v1/orders/` - List user's orders
- `GET /api/v1/orders/farmer/my-orders` - List farmer's orders
- `PATCH /api/v1/orders/{id}/status` - Update order status (farmer)
- `POST /api/v1/orders/{id}/pay` - Pay for order

### Payments
- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/` - List payments
- `GET /api/v1/payments/{id}` - Get payment details
