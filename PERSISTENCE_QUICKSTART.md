# Procur Persistence Layer - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd /Users/manaskandimalla/Desktop/Projects/procur-2
pip install -e .
```

### Step 2: Configure Database

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials (or use defaults)
# Default credentials work for local development
```

### Step 3: Setup PostgreSQL

```bash
# Make scripts executable
chmod +x scripts/setup_postgres.sh
chmod +x scripts/create_migration.sh

# Create database and user
./scripts/setup_postgres.sh
```

### Step 4: Initialize Database

```bash
# Create tables
python scripts/init_db.py

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Step 5: Run Example

```bash
# Run the database usage example
python examples/database_usage_example.py
```

You should see output showing:
- ✅ User account created
- ✅ Procurement request created
- ✅ Vendor profiles created
- ✅ Negotiation sessions started
- ✅ Offers generated and accepted
- ✅ Contract created
- ✅ All data persisted to database

## 📊 What Was Created

### Database Infrastructure

```
src/procur/db/
├── __init__.py              # Package exports
├── base.py                  # SQLAlchemy base and mixins
├── config.py                # Database configuration
├── session.py               # Session management & connection pooling
├── models.py                # ORM models (8 tables)
└── repositories/            # Data access layer
    ├── __init__.py
    ├── base.py              # Base repository with CRUD
    ├── user_repository.py
    ├── request_repository.py
    ├── vendor_repository.py
    ├── offer_repository.py
    ├── contract_repository.py
    ├── negotiation_repository.py
    ├── audit_repository.py
    └── policy_repository.py
```

### Database Tables

1. **user_accounts** - User authentication and authorization
2. **requests** - Procurement requests
3. **vendor_profiles** - Vendor information and capabilities
4. **offers** - Negotiation offers
5. **contracts** - Finalized agreements
6. **negotiation_sessions** - Negotiation tracking
7. **audit_logs** - Comprehensive audit trail
8. **policy_configs** - Policy configuration storage

### Migration System

```
alembic/
├── env.py                   # Alembic environment
├── script.py.mako           # Migration template
└── versions/                # Migration files
    └── .gitkeep
```

### Helper Scripts

```
scripts/
├── init_db.py               # Initialize database
├── setup_postgres.sh        # PostgreSQL setup
└── create_migration.sh      # Create new migration
```

## 💡 Basic Usage

### Create a User

```python
from procur.db import get_session
from procur.db.repositories import UserRepository

with get_session() as session:
    user_repo = UserRepository(session)
    user = user_repo.create(
        email="buyer@company.com",
        username="buyer1",
        hashed_password="hashed_pwd",
        full_name="John Buyer",
        role="buyer",
        organization_id="acme-corp",
    )
    print(f"Created user: {user.email}")
```

### Create a Request

```python
from procur.db.repositories import RequestRepository

with get_session() as session:
    request_repo = RequestRepository(session)
    request = request_repo.create(
        request_id="req-001",
        user_id=user.id,
        description="Need CRM for 50 users",
        request_type="saas",
        category="crm",
        budget_max=60000.0,
        quantity=50,
        status="pending",
    )
```

### Query Data

```python
# Get user by email
user = user_repo.get_by_email("buyer@company.com")

# Get all requests for user
requests = request_repo.get_by_user(user.id)

# Get vendors by category
vendors = vendor_repo.get_by_category("crm")

# Get accepted offers
offers = offer_repo.get_accepted_offers(request.id)
```

### Track Negotiations

```python
from procur.db.repositories import NegotiationRepository

with get_session() as session:
    neg_repo = NegotiationRepository(session)
    
    # Create session
    session = neg_repo.create(
        session_id="neg-001",
        request_id=request.id,
        vendor_id=vendor.id,
        status="active",
    )
    
    # Increment round
    neg_repo.increment_round(session.id)
    
    # Complete negotiation
    neg_repo.complete_session(
        session.id,
        outcome="accepted",
        savings_achieved=5000.0,
    )
```

## 🔧 Common Commands

### Database Operations

```bash
# Initialize database
python scripts/init_db.py

# Create migration
alembic revision --autogenerate -m "Add column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### PostgreSQL Commands

```bash
# Connect to database
psql -U procur_user -d procur

# List tables
\dt

# Describe table
\d user_accounts

# Query data
SELECT * FROM user_accounts;

# Exit
\q
```

## 🎯 Key Features

### ✅ Connection Pooling
- Configurable pool size (default: 5)
- Max overflow connections (default: 10)
- Automatic connection recycling
- Pool timeout handling

### ✅ Repository Pattern
- Clean separation of concerns
- Reusable CRUD operations
- Business logic encapsulation
- Easy testing and mocking

### ✅ Soft Deletes
- Records marked as deleted, not removed
- Preserves data integrity
- Audit trail maintained
- Easy recovery

### ✅ Timestamps
- Automatic created_at and updated_at
- UTC timezone for consistency
- Audit trail support

### ✅ Relationships
- Foreign key constraints
- Cascade operations
- Eager/lazy loading support
- Join optimization

### ✅ JSON Fields
- Flexible schema for specs
- Store complex data structures
- PostgreSQL JSONB support
- Queryable JSON data

### ✅ Audit Logging
- Every action logged
- User tracking
- Change tracking
- IP and user agent capture

## 📚 Next Steps

1. **Integrate with Existing Code**
   - Update `BuyerAgent` to persist negotiations
   - Store offers in database during negotiation
   - Save contracts after acceptance

2. **Add Authentication**
   - Implement password hashing (bcrypt)
   - Create JWT token generation
   - Add login/logout endpoints

3. **Build REST API**
   - Create FastAPI application
   - Add endpoints using repositories
   - Implement authentication middleware

4. **Add Monitoring**
   - Database connection metrics
   - Query performance tracking
   - Error rate monitoring

5. **Implement Caching**
   - Redis for frequently accessed data
   - Cache vendor profiles
   - Cache policy configurations

## 🆘 Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql@15

# Check connection settings in .env
cat .env
```

### Migration Conflicts

```bash
# Check current version
alembic current

# View history
alembic history

# Downgrade and re-upgrade
alembic downgrade -1
alembic upgrade head
```

### Import Errors

```bash
# Reinstall package
pip install -e .

# Verify installation
python -c "from procur.db import init_db; print('OK')"
```

## 📖 Full Documentation

See `DATABASE_README.md` for comprehensive documentation including:
- Complete schema reference
- Advanced usage patterns
- Performance optimization
- Security best practices
- Production deployment guide
- Backup and recovery procedures

## 🎉 Success!

You now have a fully functional persistence layer with:
- ✅ PostgreSQL database
- ✅ SQLAlchemy ORM models
- ✅ Alembic migrations
- ✅ Repository pattern
- ✅ Connection pooling
- ✅ Audit logging
- ✅ Comprehensive documentation

All negotiation data, offers, contracts, and audit trails are now persisted to the database!
