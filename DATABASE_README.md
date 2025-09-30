# Procur Database Persistence Layer

## Overview

This document describes the comprehensive persistence layer implementation for the Procur procurement platform. The persistence layer provides PostgreSQL database integration with SQLAlchemy ORM, Alembic migrations, connection pooling, and a repository pattern for data access.

## Architecture

### Components

1. **Database Configuration** (`src/procur/db/config.py`)
   - Environment-based configuration using Pydantic
   - Connection pooling settings
   - Database URL generation

2. **Session Management** (`src/procur/db/session.py`)
   - SQLAlchemy engine creation and lifecycle
   - Connection pooling with configurable limits
   - Session factory with context managers
   - Event listeners for monitoring

3. **ORM Models** (`src/procur/db/models.py`)
   - Complete SQLAlchemy models for all entities
   - Timestamp and soft-delete mixins
   - Relationships and foreign keys
   - JSON fields for flexible data storage

4. **Repository Layer** (`src/procur/db/repositories/`)
   - Repository pattern for clean data access
   - Base repository with common CRUD operations
   - Specialized repositories for each entity type
   - Business logic methods

5. **Alembic Migrations** (`alembic/`)
   - Database schema versioning
   - Automatic migration generation
   - Upgrade and downgrade support

## Database Schema

### Tables

#### `user_accounts`
User authentication and authorization.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `email`: Unique email address (indexed)
- `username`: Unique username (indexed)
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `role`: User role (buyer, approver, admin, vendor)
- `is_active`: Account active status
- `is_superuser`: Superuser flag
- `organization_id`: Organization identifier (indexed)
- `team`: Team name
- `last_login_at`: Last login timestamp
- `preferences`: JSON field for user preferences
- `created_at`, `updated_at`: Timestamps
- `deleted_at`: Soft delete timestamp

#### `requests`
Procurement requests from buyers.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `request_id`: Unique request identifier (indexed)
- `user_id` (FK): User who created the request
- `description`: Request description
- `request_type`: Type of request
- `category`: Product/service category (indexed)
- `budget_min`, `budget_max`: Budget range
- `quantity`: Number of units
- `billing_cadence`: Billing frequency
- `must_haves`: JSON array of required features
- `nice_to_haves`: JSON array of optional features
- `compliance_requirements`: JSON array of compliance needs
- `specs`: JSON object for additional specifications
- `status`: Request status (pending, approved, etc.) (indexed)
- `approved_at`: Approval timestamp
- `approved_by` (FK): User who approved
- `created_at`, `updated_at`, `deleted_at`: Timestamps

#### `vendor_profiles`
Vendor information and capabilities.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `vendor_id`: Unique vendor identifier (indexed)
- `name`: Vendor name (indexed)
- `website`: Vendor website URL
- `description`: Vendor description
- `category`: Vendor category (indexed)
- `list_price`: Base pricing
- `price_tiers`: JSON object for tiered pricing
- `currency`: Currency code (default: USD)
- `features`: JSON array of features
- `integrations`: JSON array of integrations
- `certifications`: JSON array of certifications
- `compliance_frameworks`: JSON array of compliance
- `guardrails`: JSON object for pricing guardrails
- `exchange_policy`: JSON object for negotiation policies
- `rating`: Vendor rating
- `review_count`: Number of reviews
- `metadata`: JSON object for additional data
- `confidence_score`: Data quality score
- `data_source`: Source of vendor data
- `last_enriched_at`: Last data enrichment timestamp
- `created_at`, `updated_at`, `deleted_at`: Timestamps

#### `offers`
Negotiation offers between buyers and vendors.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `offer_id`: Unique offer identifier (indexed)
- `request_id` (FK): Associated request
- `vendor_id` (FK): Vendor making the offer
- `negotiation_session_id` (FK): Associated negotiation session
- `unit_price`: Price per unit
- `quantity`: Number of units
- `term_months`: Contract term length
- `payment_terms`: Payment terms (NET30, NET15, etc.)
- `currency`: Currency code
- `discount_percent`: Discount percentage
- `value_adds`: JSON array of value-added services
- `conditions`: JSON array of conditions
- `score`: Offer score
- `utility_buyer`: Buyer utility score
- `utility_seller`: Seller utility score
- `tco`: Total cost of ownership
- `accepted`: Acceptance flag
- `rejected`: Rejection flag
- `round_number`: Negotiation round
- `actor`: Actor who made the offer (buyer/seller)
- `rationale`: JSON array of rationale
- `strategy`: Negotiation strategy used
- `created_at`, `updated_at`, `deleted_at`: Timestamps

#### `contracts`
Finalized contracts and agreements.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `contract_id`: Unique contract identifier (indexed)
- `request_id` (FK): Associated request
- `vendor_id` (FK): Vendor in contract
- `final_offer_id` (FK): Final accepted offer
- `unit_price`, `quantity`, `term_months`: Contract terms
- `payment_terms`: Payment terms
- `total_value`: Total contract value
- `currency`: Currency code
- `start_date`, `end_date`: Contract period
- `renewal_date`: Renewal date
- `auto_renew`: Auto-renewal flag
- `document_url`: Contract document URL
- `document_hash`: Document hash for integrity
- `template_version`: Contract template version
- `signed_by_buyer`, `signed_by_vendor`: Signature flags
- `buyer_signature_date`, `vendor_signature_date`: Signature timestamps
- `docusign_envelope_id`: DocuSign envelope ID
- `status`: Contract status (draft, active, expired) (indexed)
- `purchase_order_id`: ERP purchase order ID
- `erp_sync_status`: ERP synchronization status
- `erp_synced_at`: ERP sync timestamp
- `value_adds`: JSON array of value-added services
- `special_terms`: JSON object for special terms
- `created_at`, `updated_at`, `deleted_at`: Timestamps

#### `negotiation_sessions`
Negotiation session tracking.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `session_id`: Unique session identifier (indexed)
- `request_id` (FK): Associated request
- `vendor_id` (FK): Vendor in negotiation
- `status`: Session status (active, completed) (indexed)
- `current_round`: Current negotiation round
- `max_rounds`: Maximum allowed rounds
- `outcome`: Negotiation outcome
- `outcome_reason`: Reason for outcome
- `final_offer_id` (FK): Final offer
- `buyer_state`: JSON object for buyer state
- `seller_state`: JSON object for seller state
- `opponent_model`: JSON object for opponent modeling
- `started_at`: Session start timestamp
- `completed_at`: Session completion timestamp
- `total_messages`: Total message count
- `savings_achieved`: Savings amount
- `created_at`, `updated_at`, `deleted_at`: Timestamps
- **Unique Constraint:** (request_id, vendor_id)

#### `audit_logs`
Comprehensive audit trail for all actions.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `user_id` (FK): User who performed action
- `actor_type`: Type of actor (user, system, agent)
- `actor_id`: Actor identifier
- `action`: Action performed (indexed)
- `resource_type`: Type of resource (indexed)
- `resource_id`: Resource identifier (indexed)
- `negotiation_session_id` (FK): Associated session
- `event_data`: JSON object for event data
- `changes`: JSON object for changes made
- `ip_address`: IP address
- `user_agent`: User agent string
- `created_at`: Timestamp (no updates for audit logs)

#### `policy_configs`
Policy configuration storage.

**Columns:**
- `id` (PK): Auto-incrementing integer
- `policy_name`: Policy name (indexed)
- `policy_type`: Policy type (indexed)
- `organization_id`: Organization identifier (indexed)
- `policy_data`: JSON object for policy configuration
- `version`: Policy version number
- `is_active`: Active status flag
- `description`: Policy description
- `created_by` (FK): User who created policy
- `created_at`, `updated_at`, `deleted_at`: Timestamps
- **Unique Constraint:** (policy_name, organization_id, version)

## Installation

### Prerequisites

1. **PostgreSQL 12+**
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Ubuntu/Debian
   sudo apt-get install postgresql-15
   sudo systemctl start postgresql
   ```

2. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

### Setup Steps

#### 1. Install Dependencies

```bash
cd /Users/manaskandimalla/Desktop/Projects/procur-2
pip install -e .
```

This installs:
- `sqlalchemy>=2.0` - ORM and database toolkit
- `alembic>=1.13` - Database migration tool
- `psycopg2-binary>=2.9` - PostgreSQL adapter
- `python-dotenv>=1.0` - Environment variable management

#### 2. Configure Database

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
PROCUR_DB_HOST=localhost
PROCUR_DB_PORT=5432
PROCUR_DB_DATABASE=procur
PROCUR_DB_USERNAME=procur_user
PROCUR_DB_PASSWORD=your_secure_password_here

PROCUR_DB_POOL_SIZE=5
PROCUR_DB_MAX_OVERFLOW=10
PROCUR_DB_POOL_TIMEOUT=30
PROCUR_DB_POOL_RECYCLE=3600

PROCUR_DB_ECHO=false
```

#### 3. Create Database

Run the setup script:

```bash
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

Or manually:

```bash
psql -U postgres
CREATE USER procur_user WITH PASSWORD 'your_password';
CREATE DATABASE procur OWNER procur_user;
GRANT ALL PRIVILEGES ON DATABASE procur TO procur_user;
\q
```

#### 4. Initialize Database

```bash
python scripts/init_db.py
```

#### 5. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Usage

### Basic Database Operations

#### 1. Initialize Database Connection

```python
from procur.db import init_db, get_session

# Initialize database (one-time setup)
db = init_db(create_tables=True)

# Get a database session
with get_session() as session:
    # Your database operations here
    pass
```

#### 2. Using Repositories

```python
from procur.db import get_session
from procur.db.repositories import (
    UserRepository,
    RequestRepository,
    VendorRepository,
    OfferRepository,
    ContractRepository,
    NegotiationRepository,
    AuditRepository,
)

with get_session() as session:
    # User operations
    user_repo = UserRepository(session)
    user = user_repo.create(
        email="buyer@company.com",
        username="buyer1",
        hashed_password="hashed_password_here",
        full_name="John Buyer",
        role="buyer",
        organization_id="acme-corp",
    )
    
    # Request operations
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
    
    # Vendor operations
    vendor_repo = VendorRepository(session)
    vendor = vendor_repo.create(
        vendor_id="salesforce",
        name="Salesforce",
        category="crm",
        list_price=150.0,
        features=["api", "mobile", "analytics"],
        certifications=["SOC2", "ISO27001"],
    )
    
    # Session automatically commits on successful exit
```

#### 3. Querying Data

```python
with get_session() as session:
    user_repo = UserRepository(session)
    
    # Get by ID
    user = user_repo.get_by_id(1)
    
    # Get by email
    user = user_repo.get_by_email("buyer@company.com")
    
    # Get all users in organization
    users = user_repo.get_by_organization("acme-corp")
    
    # Update user
    user_repo.update(user.id, full_name="John Q. Buyer")
    
    # Soft delete
    user_repo.soft_delete(user.id)
```

#### 4. Negotiation Session Tracking

```python
from procur.db.repositories import NegotiationRepository, OfferRepository

with get_session() as session:
    neg_repo = NegotiationRepository(session)
    offer_repo = OfferRepository(session)
    
    # Create negotiation session
    session_record = neg_repo.create(
        session_id="neg-001",
        request_id=request.id,
        vendor_id=vendor.id,
        status="active",
        current_round=1,
        max_rounds=8,
    )
    
    # Create offer
    offer = offer_repo.create(
        offer_id="offer-001",
        request_id=request.id,
        vendor_id=vendor.id,
        negotiation_session_id=session_record.id,
        unit_price=140.0,
        quantity=50,
        term_months=12,
        payment_terms="NET30",
        round_number=1,
        actor="seller",
    )
    
    # Increment round
    neg_repo.increment_round(session_record.id)
    
    # Complete session
    neg_repo.complete_session(
        session_record.id,
        outcome="accepted",
        final_offer_id=offer.id,
        savings_achieved=500.0,
    )
```

#### 5. Audit Logging

```python
from procur.db.repositories import AuditRepository

with get_session() as session:
    audit_repo = AuditRepository(session)
    
    # Log an action
    audit_repo.log_action(
        action="create_request",
        resource_type="request",
        resource_id="req-001",
        actor_type="user",
        user_id=user.id,
        event_data={
            "category": "crm",
            "budget": 60000.0,
        },
        ip_address="192.168.1.1",
    )
    
    # Query audit logs
    user_logs = audit_repo.get_by_user(user.id)
    resource_logs = audit_repo.get_by_resource("request", "req-001")
```

### Advanced Usage

#### Transaction Management

```python
from procur.db import get_db_session

db = get_db_session()

try:
    with db.get_session() as session:
        # Multiple operations in one transaction
        user_repo = UserRepository(session)
        request_repo = RequestRepository(session)
        
        user = user_repo.create(email="test@example.com", ...)
        request = request_repo.create(user_id=user.id, ...)
        
        # Both operations commit together
except Exception as e:
    # Automatic rollback on error
    print(f"Transaction failed: {e}")
```

#### Custom Queries

```python
from sqlalchemy import select
from procur.db.models import RequestRecord, OfferRecord

with get_session() as session:
    # Complex query with joins
    query = (
        select(RequestRecord, OfferRecord)
        .join(OfferRecord, RequestRecord.id == OfferRecord.request_id)
        .where(RequestRecord.status == "approved")
        .where(OfferRecord.accepted == True)
    )
    
    results = session.execute(query).all()
```

## Database Migrations

### Creating Migrations

#### Automatic Migration Generation

```bash
# Alembic detects model changes automatically
alembic revision --autogenerate -m "Add user preferences column"
```

Or use the helper script:

```bash
chmod +x scripts/create_migration.sh
./scripts/create_migration.sh "Add user preferences column"
```

#### Manual Migration

```bash
alembic revision -m "Custom migration"
```

Edit the generated file in `alembic/versions/`:

```python
def upgrade() -> None:
    op.add_column('user_accounts', sa.Column('phone', sa.String(20)))

def downgrade() -> None:
    op.drop_column('user_accounts', 'phone')
```

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Show current version
alembic current

# Show migration history
alembic history
```

## Configuration

### Environment Variables

All database configuration is managed through environment variables with the `PROCUR_DB_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROCUR_DB_HOST` | localhost | Database host |
| `PROCUR_DB_PORT` | 5432 | Database port |
| `PROCUR_DB_DATABASE` | procur | Database name |
| `PROCUR_DB_USERNAME` | procur_user | Database user |
| `PROCUR_DB_PASSWORD` | procur_password | Database password |
| `PROCUR_DB_POOL_SIZE` | 5 | Connection pool size |
| `PROCUR_DB_MAX_OVERFLOW` | 10 | Max overflow connections |
| `PROCUR_DB_POOL_TIMEOUT` | 30 | Pool timeout (seconds) |
| `PROCUR_DB_POOL_RECYCLE` | 3600 | Connection recycle time (seconds) |
| `PROCUR_DB_ECHO` | false | Echo SQL statements |
| `PROCUR_DB_ECHO_POOL` | false | Echo pool events |

### Programmatic Configuration

```python
from procur.db.config import DatabaseConfig

config = DatabaseConfig(
    host="db.example.com",
    port=5432,
    database="procur_prod",
    username="prod_user",
    password="secure_password",
    pool_size=10,
    max_overflow=20,
)

print(config.database_url)
# postgresql://prod_user:secure_password@db.example.com:5432/procur_prod
```

## Performance Optimization

### Connection Pooling

The persistence layer uses SQLAlchemy's connection pooling for optimal performance:

- **Pool Size**: 5 connections by default
- **Max Overflow**: 10 additional connections when needed
- **Pool Timeout**: 30 seconds before raising error
- **Pool Recycle**: Connections recycled after 1 hour

### Indexing Strategy

Key indexes for performance:

- `user_accounts`: email, username, organization_id
- `requests`: request_id, user_id, status, category
- `vendor_profiles`: vendor_id, name, category
- `offers`: offer_id, request_id, vendor_id
- `contracts`: contract_id, status
- `negotiation_sessions`: session_id, status
- `audit_logs`: action, resource_type, resource_id

### Query Optimization Tips

1. **Use indexes**: Query by indexed columns when possible
2. **Limit results**: Use pagination for large result sets
3. **Eager loading**: Use `joinedload()` for relationships
4. **Batch operations**: Use bulk insert/update for multiple records
5. **Connection reuse**: Use session context managers

## Backup and Recovery

### Backup Database

```bash
# Full backup
pg_dump -U procur_user procur > procur_backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U procur_user procur | gzip > procur_backup_$(date +%Y%m%d).sql.gz

# Schema only
pg_dump -U procur_user --schema-only procur > procur_schema.sql

# Data only
pg_dump -U procur_user --data-only procur > procur_data.sql
```

### Restore Database

```bash
# Restore from backup
psql -U procur_user procur < procur_backup_20250929.sql

# Restore from compressed backup
gunzip -c procur_backup_20250929.sql.gz | psql -U procur_user procur
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
- Ensure PostgreSQL is running: `pg_isready`
- Check connection details in `.env`
- Verify firewall settings

#### 2. Authentication Failed

```
psql: FATAL: password authentication failed
```

**Solution:**
- Verify username and password in `.env`
- Check `pg_hba.conf` for authentication method
- Reset password: `ALTER USER procur_user WITH PASSWORD 'new_password';`

#### 3. Database Does Not Exist

```
psql: FATAL: database "procur" does not exist
```

**Solution:**
- Run `./scripts/setup_postgres.sh`
- Or manually: `createdb -U postgres procur`

#### 4. Migration Conflicts

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
- Check current version: `alembic current`
- View history: `alembic history`
- Resolve conflicts manually or downgrade and re-upgrade

### Debug Mode

Enable SQL logging for debugging:

```bash
# In .env
PROCUR_DB_ECHO=true
PROCUR_DB_ECHO_POOL=true
```

Or programmatically:

```python
from procur.db.config import DatabaseConfig

config = DatabaseConfig(echo=True, echo_pool=True)
```

## Testing

### Test Database Setup

```python
import pytest
from procur.db import DatabaseSession
from procur.db.config import DatabaseConfig

@pytest.fixture
def test_db():
    """Create test database session."""
    config = DatabaseConfig(database="procur_test")
    db = DatabaseSession()
    db.config = config
    db.create_all_tables()
    
    yield db
    
    db.drop_all_tables()
    db.close()

@pytest.fixture
def session(test_db):
    """Get test database session."""
    with test_db.get_session() as session:
        yield session
```

### Example Test

```python
def test_create_user(session):
    """Test user creation."""
    from procur.db.repositories import UserRepository
    
    user_repo = UserRepository(session)
    user = user_repo.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        role="buyer",
    )
    
    assert user.id is not None
    assert user.email == "test@example.com"
    
    # Verify retrieval
    retrieved = user_repo.get_by_email("test@example.com")
    assert retrieved.id == user.id
```

## Security Best Practices

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong passwords** - Minimum 16 characters
3. **Rotate credentials regularly** - Update passwords quarterly
4. **Limit database permissions** - Grant only necessary privileges
5. **Enable SSL connections** - Use `sslmode=require` in production
6. **Audit access logs** - Monitor `audit_logs` table regularly
7. **Encrypt sensitive data** - Use application-level encryption for PII
8. **Backup regularly** - Automated daily backups with retention policy

## Production Deployment

### Recommended Configuration

```env
# Production settings
PROCUR_DB_HOST=db.production.example.com
PROCUR_DB_PORT=5432
PROCUR_DB_DATABASE=procur_prod
PROCUR_DB_USERNAME=procur_prod_user
PROCUR_DB_PASSWORD=<use-secrets-manager>

# Larger pool for production
PROCUR_DB_POOL_SIZE=20
PROCUR_DB_MAX_OVERFLOW=40
PROCUR_DB_POOL_TIMEOUT=30
PROCUR_DB_POOL_RECYCLE=1800

# Disable debug logging
PROCUR_DB_ECHO=false
PROCUR_DB_ECHO_POOL=false
```

### Health Check

```python
from procur.db import get_db_session

def check_database_health():
    """Check database connectivity."""
    try:
        db = get_db_session()
        with db.get_session() as session:
            session.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Next Steps

1. **Implement REST API** - Build FastAPI endpoints using repositories
2. **Add authentication** - Implement JWT-based auth with user accounts
3. **Create admin interface** - Build management UI for data
4. **Set up monitoring** - Add database metrics and alerting
5. **Implement caching** - Add Redis for frequently accessed data
6. **Add full-text search** - Implement PostgreSQL full-text search
7. **Create data analytics** - Build reporting queries and dashboards

## Support

For issues or questions:
- Check troubleshooting section above
- Review SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Review Alembic documentation: https://alembic.sqlalchemy.org/
- Review PostgreSQL documentation: https://www.postgresql.org/docs/

## License

Part of the Procur procurement automation platform.
