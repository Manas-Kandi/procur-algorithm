# Supabase Setup Guide for Procur Platform

## Quick Start

This guide will walk you through setting up your Procur platform with Supabase in under 30 minutes.

**Your Supabase Project:**
- **Project ID:** `uedvyexzjlovliiaawuc`
- **Project URL:** `https://uedvyexzjlovliiaawuc.supabase.co`

---

## Step 1: Access Supabase Dashboard

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Log in to your account
3. Select your project: **procur**

---

## Step 2: Execute Migration Scripts

### Option A: Using Supabase SQL Editor (Recommended)

1. In the Supabase Dashboard, navigate to **SQL Editor** in the left sidebar
2. Click **New Query**
3. Execute the migration scripts in the following order:

#### Script 1: Create Tables
```sql
-- Copy and paste the contents of:
-- supabase/migrations/01_create_tables.sql
```
Click **Run** and wait for completion (should take ~10 seconds)

#### Script 2: Create Indexes
```sql
-- Copy and paste the contents of:
-- supabase/migrations/02_create_indexes.sql
```
Click **Run** and wait for completion (should take ~5 seconds)

#### Script 3: Create Triggers
```sql
-- Copy and paste the contents of:
-- supabase/migrations/03_create_triggers.sql
```
Click **Run** and wait for completion (should take ~5 seconds)

#### Script 4: Create RLS Policies
```sql
-- Copy and paste the contents of:
-- supabase/migrations/04_create_rls_policies.sql
```
Click **Run** and wait for completion (should take ~10 seconds)

#### Script 5: Create Helper Functions
```sql
-- Copy and paste the contents of:
-- supabase/migrations/05_create_functions.sql
```
Click **Run** and wait for completion (should take ~5 seconds)

### Option B: Using psql Command Line

```bash
# Get your connection string from Supabase Dashboard > Settings > Database
# It will look like: postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres

# Execute migrations
psql "YOUR_CONNECTION_STRING" -f supabase/migrations/01_create_tables.sql
psql "YOUR_CONNECTION_STRING" -f supabase/migrations/02_create_indexes.sql
psql "YOUR_CONNECTION_STRING" -f supabase/migrations/03_create_triggers.sql
psql "YOUR_CONNECTION_STRING" -f supabase/migrations/04_create_rls_policies.sql
psql "YOUR_CONNECTION_STRING" -f supabase/migrations/05_create_functions.sql
```

---

## Step 3: Get Your API Keys

1. In Supabase Dashboard, go to **Settings** > **API**
2. Copy the following keys:
   - **Project URL:** `https://uedvyexzjlovliiaawuc.supabase.co`
   - **anon public key:** (for client-side requests)
   - **service_role key:** (for server-side admin requests)

⚠️ **Important:** Keep your `service_role` key secret! Never expose it in client-side code.

---

## Step 4: Configure Your Application

### Update Environment Variables

Create or update your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Database Direct Connection (for SQLAlchemy)
# Get this from: Settings > Database > Connection String > URI
DATABASE_URL=postgresql://postgres.uedvyexzjlovliiaawuc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Alternative: Session Mode (for long-running connections)
DATABASE_URL_SESSION=postgresql://postgres.uedvyexzjlovliiaawuc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### Python Configuration

#### Option 1: Using Supabase Python Client

```python
import os
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Example: Query requests
response = supabase.table("requests").select("*").execute()
requests = response.data

# Example: Insert a new request
new_request = supabase.table("requests").insert({
    "request_id": "req-001",
    "user_id": 1,
    "description": "Need CRM software",
    "request_type": "saas",
    "status": "pending"
}).execute()
```

#### Option 2: Using SQLAlchemy (Direct Database Access)

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use connection pooler for better performance
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use in your application
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Option 3: Using Your Existing Procur Database Layer

Update `src/procur/db/config.py`:

```python
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    host: str = "aws-0-us-east-1.pooler.supabase.com"
    port: int = 6543  # Transaction mode pooler
    database: str = "postgres"
    username: str = "postgres.uedvyexzjlovliiaawuc"
    password: str  # Set via PROCUR_DB_PASSWORD env var
    
    # Or use DATABASE_URL directly
    database_url: str | None = None
    
    class Config:
        env_prefix = "PROCUR_DB_"
```

---

## Step 5: Verify Installation

### SQL Verification

Run these queries in the Supabase SQL Editor:

```sql
-- Check all tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
-- Expected: 15 tables

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename;
-- Expected: 50+ indexes

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
-- Expected: All tables should have rowsecurity = true

-- Check functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION'
ORDER BY routine_name;
-- Expected: 15+ functions
```

### Python Verification

```python
from supabase import create_client
import os

# Test connection
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin access
)

# Test table access
try:
    # Should return empty list if no data
    result = supabase.table("organizations").select("*").execute()
    print(f"✅ Successfully connected! Found {len(result.data)} organizations")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## Step 6: Seed Initial Data (Optional)

### Create Your First Organization and User

```sql
-- Insert organization
INSERT INTO organizations (organization_id, name, plan, is_active)
VALUES ('demo-org', 'Demo Organization', 'pro', true);

-- Insert admin user (you'll need to hash the password)
INSERT INTO user_accounts (
    email, 
    username, 
    hashed_password, 
    full_name, 
    role, 
    organization_id,
    is_active,
    email_verified
)
VALUES (
    'admin@demo-org.com',
    'admin',
    '$2b$12$...',  -- Use bcrypt to hash your password
    'Admin User',
    'admin',
    'demo-org',
    true,
    true
);
```

### Using Python to Seed Data

```python
from supabase import create_client
import os
import bcrypt

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Create organization
org = supabase.table("organizations").insert({
    "organization_id": "demo-org",
    "name": "Demo Organization",
    "plan": "pro",
    "is_active": True
}).execute()

# Hash password
password = "your_secure_password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create user
user = supabase.table("user_accounts").insert({
    "email": "admin@demo-org.com",
    "username": "admin",
    "hashed_password": hashed,
    "full_name": "Admin User",
    "role": "admin",
    "organization_id": "demo-org",
    "is_active": True,
    "email_verified": True
}).execute()

print(f"✅ Created organization: {org.data}")
print(f"✅ Created user: {user.data}")
```

---

## Step 7: Enable Real-Time (Optional)

For live negotiation updates:

```sql
-- Enable real-time on negotiation_events table
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_events;
ALTER PUBLICATION supabase_realtime ADD TABLE offers;
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_sessions;
```

### Subscribe to Real-Time Events in Python

```python
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Subscribe to negotiation events
def handle_event(payload):
    print(f"New event: {payload}")

supabase.table("negotiation_events").on("INSERT", handle_event).subscribe()
```

---

## Step 8: Configure Storage (Optional)

For contract document storage:

1. Go to **Storage** in Supabase Dashboard
2. Click **New Bucket**
3. Create bucket named `contracts`
4. Set as **Private**
5. Add RLS policies:

```sql
-- Allow users to upload contracts for their organization
CREATE POLICY "Users can upload contracts for their org"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'contracts' AND
    auth.uid() IN (
        SELECT id::TEXT FROM user_accounts 
        WHERE organization_id = (
            SELECT organization_id FROM user_accounts 
            WHERE id = auth.uid()::INTEGER
        )
    )
);

-- Allow users to view contracts for their organization
CREATE POLICY "Users can view contracts for their org"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'contracts' AND
    auth.uid() IN (
        SELECT id::TEXT FROM user_accounts 
        WHERE organization_id = (
            SELECT organization_id FROM user_accounts 
            WHERE id = auth.uid()::INTEGER
        )
    )
);
```

---

## Connection Pooling Best Practices

### Supabase Connection Modes

Supabase provides two connection modes:

1. **Transaction Mode (Port 6543)** - Recommended for serverless/short connections
   - Use for: API routes, serverless functions, connection pooling
   - Max connections: Higher limit
   
2. **Session Mode (Port 5432)** - For long-running connections
   - Use for: Background workers, long-running processes
   - Max connections: Lower limit

### Recommended Configuration

```python
# For API/Web Server (Transaction Mode)
DATABASE_URL = "postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300  # Recycle connections every 5 minutes
)

# For Background Workers (Session Mode)
DATABASE_URL_SESSION = "postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

engine_worker = create_engine(
    DATABASE_URL_SESSION,
    pool_size=2,
    max_overflow=3,
    pool_pre_ping=True
)
```

---

## Monitoring and Maintenance

### Supabase Dashboard Metrics

Monitor these metrics in the Dashboard:

1. **Database** > **Database Health**
   - Connection count
   - Database size
   - Query performance

2. **API** > **API Logs**
   - Request rates
   - Error rates
   - Slow queries

3. **Storage** > **Usage**
   - Storage size
   - Bandwidth usage

### Maintenance Queries

```sql
-- Clean up expired sessions (run daily)
SELECT cleanup_expired_sessions();

-- Archive old negotiations (run monthly)
SELECT archive_old_sessions(365);

-- Get organization metrics
SELECT * FROM get_organization_metrics('demo-org');

-- Check database size
SELECT 
    pg_size_pretty(pg_database_size('postgres')) as database_size,
    pg_size_pretty(pg_total_relation_size('requests')) as requests_size,
    pg_size_pretty(pg_total_relation_size('offers')) as offers_size;
```

---

## Troubleshooting

### Common Issues

#### 1. "permission denied for table X"

**Solution:** Ensure RLS policies are created and you're using the correct authentication.

```sql
-- Check RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Temporarily disable RLS for testing (NOT for production)
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
```

#### 2. "connection pool exhausted"

**Solution:** Increase pool size or use transaction mode pooler.

```python
# Increase pool size
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=40)
```

#### 3. "function does not exist"

**Solution:** Ensure all migration scripts were executed in order.

```sql
-- Check installed functions
SELECT routine_name FROM information_schema.routines 
WHERE routine_schema = 'public';
```

#### 4. "relation does not exist"

**Solution:** Verify table creation script was executed.

```sql
-- List all tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

---

## Security Checklist

- [ ] RLS enabled on all tables
- [ ] Service role key stored securely (never in client code)
- [ ] Connection strings use environment variables
- [ ] SSL/TLS enabled for database connections
- [ ] API keys rotated regularly
- [ ] Audit logs reviewed periodically
- [ ] Backup strategy configured
- [ ] Rate limiting enabled (in Supabase settings)

---

## Performance Optimization

### Indexes

All necessary indexes are created by the migration scripts. Monitor slow queries:

```sql
-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Caching Strategy

Consider implementing Redis for:
- Vendor profile lookups
- User session data
- Frequently accessed policies

### Query Optimization

```python
# Use select() to limit columns
supabase.table("requests").select("id, status, created_at").execute()

# Use filters to reduce data transfer
supabase.table("requests").select("*").eq("status", "pending").execute()

# Use pagination for large datasets
supabase.table("requests").select("*").range(0, 99).execute()
```

---

## Next Steps

1. ✅ Complete migration scripts
2. ✅ Verify installation
3. ⏳ Seed initial data
4. ⏳ Update application configuration
5. ⏳ Test authentication flow
6. ⏳ Deploy application
7. ⏳ Set up monitoring alerts
8. ⏳ Configure backups

---

## Support and Resources

- **Supabase Documentation:** https://supabase.com/docs
- **Supabase Discord:** https://discord.supabase.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Procur Architecture:** See `docs/architecture.md`
- **Migration Plan:** See `SUPABASE_MIGRATION_PLAN.md`

---

**Last Updated:** 2025-10-07  
**Version:** 1.0
