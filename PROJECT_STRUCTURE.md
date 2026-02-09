# Farmart - Complete Documentation

## 📋 Project Overview

Farmart is a full-stack e-commerce platform connecting farmers directly with buyers.

**Tech Stack:**
- **Backend**: FastAPI (Python) with SQLModel, SQLite, JWT Authentication
- **Frontend**: React 18 with Vite, Zustand, Tailwind CSS

---

## 🏗️ Complete Project Structure

```
farmart/
├── backend/
│   ├── alembic/                          # Database migrations
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── api/v1/                       # API Route handlers
│   │   │   ├── auth.py                   # Authentication endpoints
│   │   │   ├── animals.py                # Animal CRUD endpoints
│   │   │   ├── cart.py                   # Shopping cart endpoints
│   │   │   ├── orders.py                 # Order management endpoints
│   │   │   ├── payments.py              # Payment processing endpoints
│   │   │   └── users.py                  # User profile endpoints
│   │   ├── core/
│   │   │   ├── config.py                 # Settings/environment
│   │   │   ├── database.py              # Database connection
│   │   │   └── security.py              # JWT/password handling
│   │   ├── models/                       # SQLModel database models
│   │   │   ├── user.py                  # User & Farmer models
│   │   │   ├── animal.py                # Animal model
│   │   │   ├── cart.py                  # CartItem model
│   │   │   ├── order.py                 # Order & OrderItem models
│   │   │   └── payment.py               # Payment model
│   │   ├── schemas/                      # Pydantic DTOs
│   │   │   ├── user.py
│   │   │   ├── animal.py
│   │   │   ├── auth.py
│   │   │   ├── cart.py
│   │   │   ├── order.py
│   │   │   └── payment.py
│   │   ├── services/                     # Business logic
│   │   │   ├── animal_service.py
│   │   │   ├── cart_service.py
│   │   │   ├── order_service.py
│   │   │   └── payment_service.py
│   │   └── main.py                       # FastAPI app entry
│   ├── seed_data.py                      # Database seeding
│   ├── farmart.db                        # SQLite database
│   ├── .env                              # Environment variables
│   └── .requirements.txt                 # Python dependencies
│
└── frontend/Farm/my-react-app/
    ├── src/
    │   ├── api/
    │   │   └── client.js                 # Axios client with interceptors
    │   ├── app/
    │   │   └── App.jsx                   # Main app with routing
    │   ├── auth/
    │   │   ├── AuthInitializer.jsx       # Auth bootstrap
    │   │   ├── RequireAuth.jsx           # Route guard
    │   │   └── RequireRole.jsx           # Role guard
    │   ├── components/
    │   │   ├── AnimalCard.jsx
    │   │   ├── LoadingSpinner.jsx
    │   │   └── Navbar.jsx
    │   ├── context/
    │   │   └── AuthContext.jsx
    │   ├── hooks/
    │   │   └── useAuth.js
    │   ├── pages/
    │   │   ├── auth/Login.jsx
    │   │   ├── auth/Register.jsx
    │   │   ├── buyer/Marketplace.jsx
    │   │   ├── farmer/Dashboard.jsx
    │   │   ├── farmer/Home.jsx
    │   │   ├── farmer/Inventory.jsx
    │   │   ├── farmer/Orders.jsx
    │   │   ├── AnimalList.jsx
    │   │   ├── Cart.jsx
    │   │   ├── CartSuccess.jsx
    │   │   ├── Homepage.jsx
    │   │   ├── Login.jsx
    │   │   └── Register.jsx
    │   ├── store/
    │   │   ├── auth.store.js             # Zustand auth store
    │   │   └── auth.slice.js             # Redux auth slice
    │   ├── styles/
    │   │   └── index.css
    │   ├── main.jsx
    │   └── index.css
    ├── public/
    │   └── favicon.svg
    ├── .env
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── test-api.html                    # API testing page
```

---

## 🔐 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Farmer | farmer@test.com | password123 |
| Farmer 2 | farmer2@test.com | password123 |
| Buyer | buyer@test.com | password123 |
| Buyer 2 | buyer2@test.com | password123 |

---

## 🌐 Complete API Endpoints

### Base URL: `http://localhost:8000/api/v1`

---

### AUTHENTICATION (`/auth`)

#### POST `/auth/register`
Register a new user.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "name": "string",
  "role": "user" | "farmer"  // optional, defaults to "user"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

#### POST `/auth/login`
Login with email and password (form data required).

**Request (Form Data):**
```
username: email@example.com
password: password123
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

#### POST `/auth/refresh`
Refresh access token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200):**
```json
{
  "access_token": "new_token",
  "refresh_token": "new_refresh",
  "token_type": "bearer"
}
```

---

### USERS (`/users`)

#### GET `/users/me`
Get current user's profile.

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

#### PATCH `/users/me`
Update current user's profile.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "New Name",  // optional
  "password": "newpassword"  // optional
}
```

---

#### GET `/users/me/farmer`
Get farmer profile (farmers only).

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
{
  "user_id": 1,
  "farm_name": "Green Valley Farm",
  "phone": "555-0123",
  "location": "Montana",
  "bio": "Organic cattle farm"
}
```

---

#### PATCH `/users/me/farmer`
Update farmer profile.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "farm_name": "Updated Farm",
  "phone": "555-9999",
  "location": "Oregon",
  "bio": "Updated bio"
}
```

---

#### GET `/users/`
List all users (admin).

---

### ANIMALS (`/animals`)

#### GET `/animals/`
List animals with optional filters.

**Query Parameters:**
- `available_only` (bool, default: true)
- `species` (string, optional) - e.g., "Cattle", "Sheep", "Poultry", "Pigs"
- `breed` (string, optional)
- `min_age` (int, optional) - in months
- `max_age` (int, optional) - in months
- `search` (string, optional) - search in name/description

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Premium Angus Cattle",
    "species": "Cattle",
    "breed": "Angus",
    "age": 24,
    "gender": "male",
    "price": 2800.0,
    "available": true,
    "farmer_id": 1,
    "description": "High-quality Angus cattle",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

#### GET `/animals/{id}`
Get single animal by ID.

---

#### POST `/animals/`
Create new animal (farmer only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "New Animal",
  "species": "Cattle",
  "breed": "Hereford",
  "age": 12,
  "gender": "female",
  "price": 2500.0,
  "available": true,
  "description": "Description here"
}
```

---

#### PATCH `/animals/{id}`
Update animal (owner farmer only).

**Headers:** `Authorization: Bearer {token}`

---

#### DELETE `/animals/{id}`
Delete animal (owner farmer only).

---

#### GET `/animals/farmer/my-animals`
List current farmer's animals.

**Headers:** `Authorization: Bearer {token}`

---

### CART (`/cart`)

#### GET `/cart/`
Get cart items (buyer only).

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
[
  {
    "id": 1,
    "buyer_id": 1,
    "animal_id": 1,
    "quantity": 1,
    "price": 2800.0,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

#### POST `/cart/`
Add item to cart (buyer only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "animal_id": 1,
  "quantity": 1
}
```

---

#### PATCH `/cart/{id}`
Update cart item quantity (buyer only).

---

#### DELETE `/cart/{id}`
Remove item from cart (buyer only).

---

#### DELETE `/cart/`
Clear all cart items (buyer only).

---

### ORDERS (`/orders`)

#### POST `/orders/checkout`
Create order from cart (buyer only).

**Headers:** `Authorization: Bearer {token}`

**Response (201):**
```json
{
  "id": 1,
  "buyer_id": 1,
  "total_price": 2800.0,
  "status": "pending",
  "is_paid": false,
  "created_at": "2024-01-01T00:00:00",
  "items": [...]
}
```

---

#### GET `/orders/`
List buyer's orders.

**Headers:** `Authorization: Bearer {token}`

---

#### GET `/orders/farmer/my-orders`
List orders containing farmer's animals.

**Headers:** `Authorization: Bearer {token}`

**Response (200):**
```json
[
  {
    "id": 1,
    "buyer_id": 2,
    "total_price": 2800.0,
    "status": "pending",
    "is_paid": false,
    "created_at": "2024-01-01T00:00:00",
    "items": [...]
  }
]
```

---

#### PATCH `/orders/{id}/status`
Update order status (farmer only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "status": "confirmed" | "rejected"
}
```

**Status Flow:** `pending` → `confirmed`/`rejected` → `paid` (after payment)

---

#### POST `/orders/{id}/pay`
Mark order as paid (buyer only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "method": "M-Pesa"
}
```

---

### PAYMENTS (`/payments`)

#### POST `/payments/`
Create payment for order (buyer only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "order_id": 1,
  "amount": 2800.0,
  "method": "M-Pesa"
}
```

---

#### GET `/payments/`
List user's payments.

**Headers:** `Authorization: Bearer {token}`

---

#### GET `/payments/{id}`
Get specific payment.

---

#### PATCH `/payments/{id}`
Update payment status.

---

#### POST `/payments/{id}/complete`
Mark payment as completed.

---

## 📊 Data Models

### User
```python
id: int
email: str (unique)
name: str
password_hash: str
role: str  # "user" or "farmer"
is_active: bool
created_at: datetime
```

### Farmer
```python
user_id: int (FK)
farm_name: str
phone: str
location: str
bio: str
```

### Animal
```python
id: int
name: str
species: str  # Cattle, Sheep, Poultry, Pigs
breed: str
age: int  # months
gender: str  # male, female
price: float
available: bool
farmer_id: int (FK)
description: str
created_at: datetime
```

### CartItem
```python
id: int
buyer_id: int (FK)
animal_id: int (FK)
quantity: int
price: float  # snapshot of animal price
created_at: datetime
```

### Order
```python
id: int
buyer_id: int (FK)
total_price: float
status: str  # pending, confirmed, rejected, paid, completed
is_paid: bool
created_at: datetime
```

### OrderItem
```python
id: int
order_id: int (FK)
animal_id: int (FK)
quantity: int
price: float
```

### Payment
```python
id: int
order_id: int (FK)
amount: float
method: str  # M-Pesa, etc.
status: str  # pending, completed, failed
transaction_id: str
created_at: datetime
```

---

## 🔄 Data Flow

### Authentication Flow
```
1. User POST /auth/login (form data: username, password)
2. Backend validates credentials
3. Returns JWT access_token + refresh_token
4. Frontend stores tokens in localStorage
5. All requests include: Authorization: Bearer {token}
6. On app load: GET /users/me to restore session
```

### Cart → Order Flow
```
1. Browse animals → GET /animals/
2. Add to cart → POST /cart/
3. View cart → GET /cart/
4. Checkout → POST /orders/checkout
   - Creates Order from cart items
   - Marks animals as unavailable
   - Clears cart
5. Farmer sees order → GET /orders/farmer/my-orders
6. Farmer confirms → PATCH /orders/{id}/status (status: "confirmed")
7. Buyer pays → POST /orders/{id}/pay
```

---

## 🚀 Running the Application

### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
cd frontend/Farm/my-react-app
npm run dev
```

### Access Points
- **Frontend App**: http://localhost:5173
- **API Test Page**: http://localhost:5173/test-api.html
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

---

## 🧪 Testing with test-api.html

1. Open http://localhost:5173/test-api.html
2. Click **"Login as Farmer"** or **"Login as Buyer"**
3. Use the sections to test:
   - **Available Animals** - View all animals
   - **Cart** - Add items, checkout (buyer)
   - **Your Orders** - View orders, pay (buyer)
   - **Orders for Your Animals** - Confirm/reject (farmer)
   - **Response Log** - See all API calls

---

## 📁 Key Files

### Backend
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app factory, middleware, router mounting |
| `app/core/config.py` | Environment variables, settings |
| `app/core/database.py` | Async SQLAlchemy engine, sessions |
| `app/core/security.py` | JWT tokens, password hashing |
| `app/api/v1/*.py` | API endpoints |
| `app/models/*.py` | Database tables |
| `app/schemas/*.py` | Request/response validation |
| `app/services/*.py` | Business logic |

### Frontend
| File | Purpose |
|------|---------|
| `src/api/client.js` | Axios instance with interceptors |
| `src/store/auth.store.js` | Zustand auth state management |
| `src/auth/RequireAuth.jsx` | Protects authenticated routes |
| `src/auth/RequireRole.jsx` | Protects role-specific routes |
| `src/pages/auth/Login.jsx` | Login page |
| `test-api.html` | Standalone API testing page |
