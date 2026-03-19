# 🚗 Auto Market API

A modern RESTful API system for managing an automotive marketplace. Built with FastAPI using async/await, PostgreSQL, and JWT authentication.

## 🎯 Key Features

- **Asynchronous Architecture** - leveraging SQLAlchemy async and FastAPI for maximum performance
- **JWT Authentication** - secured endpoints with access/refresh token system
- **Image Management** - upload, processing, and optimization of car and profile images
- **Category System** - organize cars by categories with pagination support
- **User Profiles** - extended profile system with bio and avatars
- **Data Validation** - strict validation through Pydantic schemas
- **Database Migrations** - database schema management via Alembic

## 🏗️ Technology Stack

- **Backend Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 18.1
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT (python-jose)
- **Image Processing**: Pillow
- **Validation**: Pydantic 2.0
- **Migrations**: Alembic
- **Dependency Management**: Poetry
- **Containerization**: Docker & Docker Compose

## 📋 Requirements

- Python 3.12+
- Poetry (dependency management)
- Docker & Docker Compose
- PostgreSQL 18.1 (automatically runs in Docker)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <https://github.com/Paul-Starodub/auto-market.git>
cd auto-market
```

> **Note**: Make sure you have Poetry installed. If not, install it with: `pip install poetry`

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database
DB__HOST=localhost
DB__PORT=5432
DB__NAME=auto_market
DB__USER=postgres
DB__PASSWORD=your_secure_password
DB__ECHO=False

# JWT Security
SECRET_KEY_ACCESS=your_access_secret_key_here_min_32_chars
SECRET_KEY_REFRESH=your_refresh_secret_key_here_min_32_chars
JWT_SIGNING_ALGORITHM=HS256

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
MAX_UPLOAD_SIZE_BYTES=5242880
ENTITIES_PER_PAGE=10
```

> **⚠️ Important**: Use strong random strings for SECRET_KEY_ACCESS and SECRET_KEY_REFRESH in production

### 3. Run with Docker

```bash
# Start PostgreSQL
docker-compose up -d

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Apply migrations
alembic upgrade head

# Run the application
python src/main.py
```

The API will be available at: **http://localhost:8000**

Swagger documentation: **http://localhost:8000/docs**

ReDoc documentation: **http://localhost:8000/redoc**

### 4. Stop Services

```bash
# Stop database
docker-compose down

# Stop with volume removal (clean database)
docker-compose down -v
```

## 📚 API Endpoints

### 🔐 Authentication (`/api/customers`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/customers/` | Register a new user | ❌ |
| POST | `/customers/login/` | Login (get tokens) | ❌ |
| POST | `/customers/refresh/` | Refresh access token | ❌ |
| POST | `/customers/logout/` | Logout (revoke refresh token) | ✅ |
| GET | `/customers/me/` | Get current user data | ✅ |
| GET | `/customers/{customer_id}/` | Get public user data | ✅ |
| PATCH | `/customers/{customer_id}/` | Update user data | ✅ |
| DELETE | `/customers/{customer_id}/` | Delete account | ✅ |

### 🖼️ Profile & Images (`/api/customers`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/customers/me/profile/` | Get user profile | ✅ |
| POST | `/customers/me/profile/` | Create profile | ✅ |
| PATCH | `/customers/me/profile/` | Update profile | ✅ |
| DELETE | `/customers/me/profile/` | Delete profile | ✅ |
| PATCH | `/customers/{customer_id}/picture/` | Upload avatar | ✅ |
| DELETE | `/customers/{customer_id}/picture/` | Delete avatar | ✅ |

### 🚗 Cars (`/api/cars`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/cars/` | List all cars | ✅ |
| GET | `/cars/{car_id}/` | Get car details | ✅ |
| POST | `/cars/` | Create new car | ✅ |
| PATCH | `/cars/{car_id}/` | Update car information | ✅ |
| DELETE | `/cars/{car_id}/` | Delete car | ✅ |

### 📸 Car Images (`/api/cars`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/cars/{car_id}/images/` | List car images | ✅ |
| POST | `/cars/{car_id}/images/` | Upload images (multiple) | ✅ |
| DELETE | `/cars/{car_id}/images/` | Delete images | ✅ |

### 📁 Categories (`/api/categories`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/categories/` | List categories with pagination | ✅ |
| GET | `/categories/{category_id}/` | Get category details | ✅ |
| POST | `/categories/` | Create new category | ✅ |
| PUT | `/categories/{category_id}/` | Update category | ✅ |
| DELETE | `/categories/{category_id}/` | Delete category | ✅ |

## 🔑 Usage Examples

### Registration and Authentication

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 2. Login to the system
curl -X POST "http://localhost:8000/api/customers/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePass123!"

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "refresh_token": "eyJhbGc...",
#   "token_type": "bearer"
# }
```

### Working with Cars

```bash
# 3. Create a car (token required)
curl -X POST "http://localhost:8000/api/cars/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Camry",
    "car_type": "passenger",
    "fuel_type": "hybrid",
    "transmission_type": "automatic",
    "start_year": 2020,
    "end_year": 2024,
    "cost": 35000.00,
    "category_id": 1
  }'

# 4. Get list of cars
curl -X GET "http://localhost:8000/api/cars/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 5. Upload car images
curl -X POST "http://localhost:8000/api/cars/1/images/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "files=@car_photo1.jpg" \
  -F "files=@car_photo2.jpg"
```

### Working with Categories

```bash
# 6. Get categories with pagination
curl -X GET "http://localhost:8000/api/categories/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 7. Create a category
curl -X POST "http://localhost:8000/api/categories/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "SUV"}'
```

## 📊 Database Structure

### Main Models

**Customers** (Users)
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Hashed password
- `image_file` - Avatar path

**Cars** (Vehicles)
- `id` - Primary key
- `brand` - Car brand
- `model` - Car model
- `car_type` - Type (PASSENGER, MOTO, TRUCK)
- `fuel_type` - Fuel type (PETROL, DIESEL, ELECTRIC, GAS, HYBRID)
- `transmission_type` - Transmission (MANUAL, AUTOMATIC, TIPTRONIC, ROBOT, CVT, REDUCER)
- `start_year` - Production start year
- `end_year` - Production end year
- `cost` - Price (DECIMAL 15,2)
- `category_id` - FK to category

**Categories**
- `id` - Primary key
- `name` - Unique category name

**Profiles** (User Profiles)
- `id` - Primary key
- `customer_id` - FK to customer (one-to-one)
- `first_name` - First name
- `last_name` - Last name
- `bio` - Biography

**CarImages** (Car Images)
- `id` - Primary key
- `file_path` - File path
- `car_id` - FK to car

**RefreshTokens** (Refresh Tokens)
- `id` - Primary key
- `token` - Unique token
- `expires_at` - Expiration timestamp
- `customer_id` - FK to customer

**CustomerCar** (Customer-Car Relationship)
- `customer_id` - FK to customer
- `car_id` - FK to car
- `offer` - Offered price

## 🔒 Security

- **JWT Tokens**: Access tokens live for 30 minutes, refresh tokens for 7 days
- **Bcrypt Hashing**: All passwords are hashed using bcrypt
- **Protected Endpoints**: All operations require authentication (except registration and login)
- **Email Validation**: Automatic email format verification
- **Upload Restrictions**: Maximum file size - 5 MB
- **Automatic Cleanup**: Old refresh tokens are automatically removed

## 🛠️ Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Project Structure

```
auto-market/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration template
├── src/
│   ├── core/                   # Core application configuration
│   │   └── config.py           # Settings and environment variables
│   ├── crud/                   # CRUD operations
│   │   ├── cars.py             # Car operations
│   │   ├── categories.py       # Category operations
│   │   └── customers.py        # Customer operations
│   ├── database/               # Database layer
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── base.py         # Base model class
│   │   │   ├── cars.py         # Car, Category, CarImage models
│   │   │   └── customers.py    # Customer, Profile, RefreshToken models
│   │   ├── validators/         # Custom validators
│   │   │   └── customers.py    # Customer field validators
│   │   ├── dependencies.py     # Database dependencies
│   │   ├── engine.py           # Database engine configuration
│   │   └── mixins.py           # Model mixins
│   ├── routes/                 # API endpoints (controllers)
│   │   ├── cars.py             # Car endpoints
│   │   ├── categories.py       # Category endpoints
│   │   └── customers.py        # Customer/auth endpoints
│   ├── schemas/                # Pydantic models (DTOs)
│   │   ├── cars.py             # Car schemas
│   │   ├── categories.py       # Category schemas
│   │   └── customers.py        # Customer schemas
│   ├── security/               # Authentication & authorization
│   │   ├── auth.py             # Auth dependencies
│   │   ├── dependencies.py     # Security dependencies
│   │   ├── passwords.py        # Password hashing
│   │   ├── token_manager.py    # JWT token management
│   │   └── utils.py            # Security utilities
│   ├── services/               # Business logic services
│   │   └── image_utils.py      # Image processing utilities
│   ├── media/                  # Uploaded media files
│   │   └── pics/               # Image storage
│   ├── static/                 # Static files (CSS, JS, default images)
│   └── main.py                 # Application entry point
├── .env                        # Environment variables (not in repo)
├── .env.template               # Environment template
├── .gitignore                  # Git ignore rules
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker services configuration
├── poetry.lock                 # Poetry lock file
├── pyproject.toml              # Poetry dependencies & project metadata
└── README.md                   # Project documentation
```

## 📝 Future Enhancements

- [ ] Add review and rating system
- [ ] Integration with external APIs (e.g., AUTO.RIA)
- [ ] Notification system (email, push)
- [ ] Advanced search and filtering
- [ ] Analytics and statistics
- [ ] Favorites system
- [ ] Buyer-seller chat
- [ ] View history

## 📄 License

MIT License

## 👨‍💻 Author

Created to demonstrate FastAPI development skills

---

**Contact**: [amorallex@gmail.com / https://github.com/Paul-Starodub]

**Year**: 2026
