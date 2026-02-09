# Farmart - Direct Farm Animal Marketplace

Farmart is an e-commerce application that connects farmers directly with buyers, eliminating middlemen from the livestock trading process.

## Tech Stack

- **Backend**: FastAPI (Python) with SQLModel and SQLite/PostgreSQL
- **Frontend**: React 18 with Vite, Redux Toolkit, Tailwind CSS
- **Authentication**: JWT with access/refresh tokens
- **State Management**: Zustand

## Features

### Farmers
- Register/Login with farmer role
- Add new animals for sale
- Update and edit animal listings
- View and manage orders
- Confirm or reject orders

### Buyers
- Register/Login with buyer role
- Browse all available animals
- Search by name and filter by species, breed, age
- Add animals to cart
- Checkout and pay for orders

## Project Structure

```
farmart/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── animals.py    # Animal CRUD
│   │   │   ├── cart.py      # Shopping cart
│   │   │   ├── orders.py     # Order management
│   │   │   ├── payments.py   # Payment processing
│   │   │   └── users.py      # User profiles
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLModel models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── seed_data.py         # Database seeding
│   └── .env                 # Environment variables
│
└── frontend/
    └── Farm/
        └── my-react-app/
            ├── src/
            │   ├── api/           # Axios client
            │   ├── app/            # App router
            │   ├── components/     # Reusable components
            │   ├── hooks/          # Custom hooks
            │   ├── pages/          # Page components
            │   │   ├── farmer/     # Farmer pages
            │   │   └── *.jsx
            │   ├── store/          # Zustand store
            │   └── styles/         # Global styles
            └── .env                # Environment variables
```

## Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
./venv/bin/pip install -r .requirements.txt

# Initialize database with seed data
./venv/bin/python seed_data.py

# Start the server
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend/Farm/my-react-app

# Install dependencies
npm install

# Start development server
npm run dev
```

## Test Accounts

After running `seed_data.py`:

| Role | Email | Password |
|------|-------|----------|
| Farmer | farmer@test.com | password123 |
| Farmer 2 | farmer2@test.com | password123 |
| Buyer | buyer@test.com | password123 |
| Buyer 2 | buyer2@test.com | password123 |

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite+aiosqlite:///./farmart.db
JWT_SECRET_KEY=your-super-secret-key
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=/api/v1
```

## Role-Based Routing

The app implements proper role-based access control:

1. **Auth Store** - Single source of truth for auth state
2. **Bootstrap** - Waits for `/me` endpoint before rendering routes
3. **Route Guards** - Blocks unauthorized access at route level
4. **No Conditional Rendering** - Components never mount if unauthorized

### Auth State Flow
```
APP LOAD
  ↓
READ TOKEN FROM ST
FETCH /ORAGE
  ↓me ENDPOINT
  ↓
RESOLVE ROLE (farmer | user)
  ↓
UPDATE AUTH STATUS
  ↓
ALLOW ROUTE RENDERING
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Animals
- `GET /api/v1/animals/` - List with filters
- `POST /api/v1/animals/` - Create (farmer only)
- `PATCH /api/v1/animals/{id}` - Update (owner only)
- `DELETE /api/v1/animals/{id}` - Delete (owner only)

### Cart
- `GET /api/v1/cart/` - List cart items
- `POST /api/v1/cart/` - Add item
- `DELETE /api/v1/cart/{id}` - Remove item

### Orders
- `POST /api/v1/orders/checkout` - Create order
- `GET /api/v1/orders/` - List my orders
- `PATCH /api/v1/orders/{id}/status` - Update status (farmer)
- `POST /api/v1/orders/{id}/pay` - Pay for order

## Development

### Running Tests
```bash
# Backend tests
cd backend
./venv/bin/pytest

# Frontend tests
cd frontend/Farm/my-react-app
npm run test
```

### Building for Production
```bash
cd frontend/Farm/my-react-app
npm run build
```

The build output will be in `dist/` directory.
