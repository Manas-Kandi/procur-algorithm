# Procur REST API Documentation

## Overview

Production-ready REST API for the Procur agentic procurement platform. Built with FastAPI, featuring JWT authentication, rate limiting, CORS support, and comprehensive OpenAPI documentation.

## Features

✅ **FastAPI Framework** - Modern, fast, async-ready
✅ **JWT Authentication** - Secure token-based auth
✅ **Role-Based Access Control** - User roles and permissions
✅ **Rate Limiting** - Prevent abuse (60 req/min, 1000 req/hour)
✅ **CORS Support** - Cross-origin resource sharing
✅ **Request Validation** - Pydantic schemas
✅ **OpenAPI/Swagger** - Auto-generated documentation
✅ **Database Integration** - PostgreSQL via SQLAlchemy
✅ **Audit Logging** - Complete API request trail
✅ **Error Handling** - Consistent error responses

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

This installs:
- `fastapi>=0.109` - Web framework
- `uvicorn[standard]>=0.27` - ASGI server
- `python-jose[cryptography]>=3.3` - JWT tokens
- `passlib[bcrypt]>=1.7` - Password hashing
- `slowapi>=0.1.9` - Rate limiting

### 2. Configure API

Update `.env` with API settings:

```env
# API Configuration
PROCUR_API_HOST=0.0.0.0
PROCUR_API_PORT=8000
PROCUR_API_SECRET_KEY=your-secret-key-here
PROCUR_API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
PROCUR_API_CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
PROCUR_API_RATE_LIMIT_ENABLED=true
PROCUR_API_RATE_LIMIT_PER_MINUTE=60
```

### 3. Start API Server

```bash
# Development mode (auto-reload)
python run_api.py

# Or with uvicorn directly
uvicorn src.procur.api.app:app --reload --host 0.0.0.0 --port 8000

# Production mode (multiple workers)
uvicorn src.procur.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "organization_id": "acme-corp"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "role": "buyer",
  "is_active": true,
  "organization_id": "acme-corp",
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "username",
  "password": "SecurePassword123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "buyer",
  "is_active": true
}
```

### Procurement Requests

#### Create Request
```http
POST /requests
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Need CRM for 50 sales reps",
  "category": "crm",
  "budget_max": 75000.0,
  "quantity": 50,
  "must_haves": ["api_access", "mobile_app"],
  "compliance_requirements": ["SOC2", "GDPR"]
}

Response: 201 Created
{
  "id": 1,
  "request_id": "req-abc123",
  "user_id": 1,
  "description": "Need CRM for 50 sales reps",
  "category": "crm",
  "budget_max": 75000.0,
  "quantity": 50,
  "status": "pending",
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### List Requests
```http
GET /requests?status=pending&limit=20&offset=0
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "request_id": "req-abc123",
    "description": "Need CRM for 50 sales reps",
    "status": "pending",
    ...
  }
]
```

#### Get Request
```http
GET /requests/{request_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "request_id": "req-abc123",
  "description": "Need CRM for 50 sales reps",
  "status": "pending",
  ...
}
```

#### Update Request
```http
PATCH /requests/{request_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "budget_max": 80000.0,
  "status": "approved"
}

Response: 200 OK
{
  "id": 1,
  "request_id": "req-abc123",
  "budget_max": 80000.0,
  "status": "approved",
  ...
}
```

#### Delete Request
```http
DELETE /requests/{request_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### Vendors

#### List Vendors
```http
GET /vendors?category=crm&limit=20
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "vendor_id": "salesforce",
    "name": "Salesforce",
    "category": "crm",
    "list_price": 150.0,
    "features": ["api_access", "mobile_app"],
    "certifications": ["SOC2", "ISO27001"],
    "rating": 4.5
  }
]
```

#### Search Vendors
```http
GET /vendors?search=salesforce
Authorization: Bearer <token>

Response: 200 OK
[...]
```

#### Get Vendor
```http
GET /vendors/{vendor_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "vendor_id": "salesforce",
  "name": "Salesforce",
  "website": "https://www.salesforce.com",
  "category": "crm",
  "list_price": 150.0,
  "features": ["api_access", "mobile_app", "reporting"],
  "certifications": ["SOC2_TYPE2", "ISO27001"],
  "rating": 4.5,
  "review_count": 15000
}
```

#### Create Vendor (Admin Only)
```http
POST /vendors
Authorization: Bearer <token>
Content-Type: application/json

{
  "vendor_id": "hubspot",
  "name": "HubSpot CRM",
  "category": "crm",
  "list_price": 120.0,
  "features": ["api_access", "mobile_app"],
  "certifications": ["SOC2"]
}

Response: 201 Created
{
  "id": 2,
  "vendor_id": "hubspot",
  "name": "HubSpot CRM",
  ...
}
```

### Negotiations

#### Get Negotiation
```http
GET /negotiations/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "session_id": "neg-xyz789",
  "request_id": 1,
  "vendor_id": 1,
  "status": "active",
  "current_round": 3,
  "max_rounds": 8,
  "total_messages": 6,
  "started_at": "2025-01-15T10:00:00Z"
}
```

#### Get Negotiation Offers
```http
GET /negotiations/{session_id}/offers
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "offer_id": "offer-001",
    "unit_price": 140.0,
    "quantity": 50,
    "term_months": 12,
    "payment_terms": "NET30",
    "round_number": 1,
    "actor": "seller",
    "accepted": false
  },
  {
    "id": 2,
    "offer_id": "offer-002",
    "unit_price": 135.0,
    "quantity": 50,
    "term_months": 24,
    "payment_terms": "NET15",
    "round_number": 3,
    "actor": "seller",
    "accepted": false
  }
]
```

#### Approve Negotiation
```http
POST /negotiations/{session_id}/approve
Authorization: Bearer <token>
Content-Type: application/json

{
  "offer_id": 2,
  "notes": "Acceptable terms, proceeding with contract"
}

Response: 200 OK
{
  "id": 1,
  "session_id": "neg-xyz789",
  "status": "completed",
  "outcome": "accepted",
  "final_offer_id": 2,
  "completed_at": "2025-01-15T11:00:00Z"
}
```

#### Reject Negotiation
```http
POST /negotiations/{session_id}/reject?reason=Price too high
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "session_id": "neg-xyz789",
  "status": "completed",
  "outcome": "rejected",
  "outcome_reason": "Price too high"
}
```

### Contracts

#### List Contracts
```http
GET /contracts?status=draft&limit=20
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "contract_id": "contract-001",
    "request_id": 1,
    "vendor_id": 1,
    "unit_price": 135.0,
    "quantity": 50,
    "term_months": 24,
    "total_value": 162000.0,
    "status": "draft",
    "signed_by_buyer": false,
    "signed_by_vendor": false
  }
]
```

#### Get Contract
```http
GET /contracts/{contract_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "contract_id": "contract-001",
  "request_id": 1,
  "vendor_id": 1,
  "unit_price": 135.0,
  "quantity": 50,
  "term_months": 24,
  "payment_terms": "NET15",
  "total_value": 162000.0,
  "currency": "USD",
  "status": "draft",
  "signed_by_buyer": false,
  "signed_by_vendor": false,
  "created_at": "2025-01-15T11:00:00Z"
}
```

#### Sign Contract
```http
POST /contracts/{contract_id}/sign
Authorization: Bearer <token>
Content-Type: application/json

{
  "signature_type": "buyer",
  "signature_data": "optional-signature-data"
}

Response: 200 OK
{
  "id": 1,
  "contract_id": "contract-001",
  "signed_by_buyer": true,
  "buyer_signature_date": "2025-01-15T12:00:00Z",
  "status": "draft"
}
```

#### Download Contract
```http
GET /contracts/{contract_id}/download
Authorization: Bearer <token>

Response: 200 OK
{
  "document_url": "https://s3.amazonaws.com/contracts/contract-001.pdf"
}
```

### Health Check

#### Health Status
```http
GET /health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

#### Root Endpoint
```http
GET /

Response: 200 OK
{
  "name": "Procur API",
  "version": "1.0.0",
  "description": "Agentic procurement automation platform API",
  "docs_url": "/docs",
  "redoc_url": "/redoc"
}
```

## Authentication

### JWT Token Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Getting a Token

1. Register a user: `POST /auth/register`
2. Login: `POST /auth/login`
3. Use the returned `access_token` in subsequent requests

### Token Expiration

- Default expiration: 30 minutes
- Configurable via `PROCUR_API_ACCESS_TOKEN_EXPIRE_MINUTES`
- Refresh by logging in again

## Authorization

### User Roles

- **buyer**: Can create requests, view vendors, manage own negotiations
- **approver**: Can approve requests and contracts
- **admin**: Full access, can create vendors
- **vendor**: Vendor-side access (future)

### Role-Based Access

Some endpoints require specific roles:

```python
# Admin only
POST /vendors  # Requires admin role

# Superuser only
DELETE /users/{id}  # Requires superuser flag
```

## Rate Limiting

### Default Limits

- **Per minute**: 60 requests
- **Per hour**: 1000 requests
- **Per IP address**: Tracked by client IP

### Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642248000
```

### Rate Limit Exceeded

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded: 60 per 1 minute"
}
```

### Configuration

```env
PROCUR_API_RATE_LIMIT_ENABLED=true
PROCUR_API_RATE_LIMIT_PER_MINUTE=60
PROCUR_API_RATE_LIMIT_PER_HOUR=1000
```

## CORS Configuration

### Allowed Origins

Configure allowed origins in `.env`:

```env
PROCUR_API_CORS_ORIGINS=["http://localhost:3000","https://app.procur.ai"]
```

### CORS Headers

The API supports:
- **Credentials**: Cookies and authorization headers
- **Methods**: All HTTP methods (GET, POST, PUT, DELETE, etc.)
- **Headers**: All headers

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "error_type",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 204 | No Content | Resource deleted |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "error_code": "validation_error"
}
```

## Request Validation

### Pydantic Schemas

All request bodies are validated using Pydantic schemas:

```python
# Example: Create Request
{
  "description": str,  # min_length=10, required
  "category": str,  # optional
  "budget_max": float,  # gt=0, optional
  "quantity": int,  # gt=0, optional
  "must_haves": List[str],  # optional
  "compliance_requirements": List[str]  # optional
}
```

### Field Validation

- **Email**: Valid email format
- **Password**: Minimum 8 characters
- **Budget**: Must be positive
- **Quantity**: Must be positive integer
- **Status**: Must be valid enum value

## Pagination

### Query Parameters

```http
GET /requests?page=1&page_size=20&offset=0&limit=20
```

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `offset`: Number of items to skip
- `limit`: Maximum items to return

### Pagination Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

## Filtering

### Query Parameters

Most list endpoints support filtering:

```http
# Filter by status
GET /requests?status=pending

# Filter by category
GET /vendors?category=crm

# Search by name
GET /vendors?search=salesforce

# Combine filters
GET /requests?status=approved&category=crm&limit=10
```

## Python Client Example

```python
import requests

class ProcurClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]
    
    def create_request(self, data):
        response = requests.post(
            f"{self.base_url}/requests",
            json=data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()

# Usage
client = ProcurClient()
client.login("username", "password")
request = client.create_request({
    "description": "Need CRM",
    "budget_max": 50000.0,
    "quantity": 50
})
```

## JavaScript/TypeScript Client Example

```typescript
class ProcurClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async login(username: string, password: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
  }

  async createRequest(data: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.token}`,
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}

// Usage
const client = new ProcurClient();
await client.login("username", "password");
const request = await client.createRequest({
  description: "Need CRM",
  budget_max: 50000.0,
  quantity: 50,
});
```

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Password123!"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Password123!"}'

# Create request (with token)
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"description":"Need CRM software","budget_max":50000,"quantity":50}'
```

### Automated Testing

```python
import pytest
from fastapi.testclient import TestClient
from src.procur.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!"
    })
    assert response.status_code == 201

def test_login():
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "Password123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Deployment

### Development

```bash
# Auto-reload on code changes
python run_api.py

# Or
uvicorn src.procur.api.app:app --reload
```

### Production

```bash
# Multiple workers
uvicorn src.procur.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
gunicorn src.procur.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "src.procur.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Variables

Production environment variables:

```env
PROCUR_API_SECRET_KEY=<generate-secure-random-key>
PROCUR_API_WORKERS=4
PROCUR_API_RELOAD=false
PROCUR_DB_HOST=db.production.com
PROCUR_DB_PASSWORD=<secure-password>
```

## Security Best Practices

1. **Change Secret Key**: Generate a secure random key for production
2. **Use HTTPS**: Always use TLS/SSL in production
3. **Rotate Tokens**: Implement token refresh mechanism
4. **Rate Limiting**: Enable and configure appropriately
5. **Input Validation**: All inputs validated via Pydantic
6. **SQL Injection**: Protected by SQLAlchemy ORM
7. **CORS**: Configure allowed origins restrictively
8. **Audit Logging**: All API requests logged

## Monitoring

### Health Endpoint

```bash
# Check API health
curl http://localhost:8000/health
```

### Metrics

- Request count
- Response times
- Error rates
- Rate limit hits
- Database connection status

### Logging

All requests logged with:
- Timestamp
- Method and path
- Status code
- Processing time
- User ID (if authenticated)
- IP address

## Troubleshooting

### API Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Check database connection
python -c "from src.procur.db import init_db; init_db()"
```

### Authentication Errors

```bash
# Verify token
python -c "from src.procur.api.security import decode_access_token; print(decode_access_token('YOUR_TOKEN'))"
```

### Database Errors

```bash
# Check database connection
psql -U procur_user -d procur -c "SELECT 1"

# Run migrations
alembic upgrade head
```

## Support

- **API Documentation**: http://localhost:8000/docs
- **Database Documentation**: See `DATABASE_README.md`
- **Issue Tracker**: GitHub Issues
- **Email**: support@procur.ai

## License

Part of the Procur procurement automation platform.
