# Supabase Database Migration for Procur Platform

This directory contains all SQL migration scripts to set up the Procur procurement platform on Supabase.

## 📋 Overview

**Supabase Project Details:**
- **Project ID:** `uedvyexzjlovliiaawuc`
- **Project URL:** `https://uedvyexzjlovliiaawuc.supabase.co`
- **Database:** PostgreSQL 15+ (Supabase managed)

## 🗂️ Migration Files

Execute these files **in order** in the Supabase SQL Editor:

| File | Description | Tables/Objects Created | Execution Time |
|------|-------------|----------------------|----------------|
| `01_create_tables.sql` | Core database schema | 15 tables | ~10 seconds |
| `02_create_indexes.sql` | Performance indexes | 50+ indexes | ~5 seconds |
| `03_create_triggers.sql` | Automatic triggers | 20+ triggers | ~5 seconds |
| `04_create_rls_policies.sql` | Row Level Security | 60+ RLS policies | ~10 seconds |
| `05_create_functions.sql` | Helper functions | 15+ functions | ~5 seconds |

**Total Execution Time:** ~35 seconds

## 📊 Database Schema

### Core Tables (15 total)

#### Authentication & Authorization
- `organizations` - Multi-tenant organization management
- `user_accounts` - User authentication with MFA support
- `user_sessions` - Active session tracking
- `api_keys` - Programmatic API access
- `password_history` - Password reuse prevention
- `login_attempts` - Security monitoring
- `oauth_connections` - SSO/OAuth integration

#### Business Logic
- `requests` - Procurement requests with structured intake
- `vendor_profiles` - Vendor catalog with capabilities
- `negotiation_sessions` - Negotiation tracking
- `offers` - Negotiation proposals with scoring
- `contracts` - Finalized agreements with e-signature

#### Operational
- `negotiation_events` - Real-time event streaming
- `audit_logs` - Immutable compliance audit trail
- `policy_configs` - Versioned policy configurations

## 🚀 Quick Start

### Step 1: Execute Migrations

```bash
# Option A: Using Supabase SQL Editor (Recommended)
# 1. Go to https://app.supabase.com
# 2. Open your project: procur
# 3. Navigate to SQL Editor
# 4. Copy and paste each file's contents
# 5. Click "Run" for each file in order

# Option B: Using psql
psql "YOUR_SUPABASE_CONNECTION_STRING" -f migrations/01_create_tables.sql
psql "YOUR_SUPABASE_CONNECTION_STRING" -f migrations/02_create_indexes.sql
psql "YOUR_SUPABASE_CONNECTION_STRING" -f migrations/03_create_triggers.sql
psql "YOUR_SUPABASE_CONNECTION_STRING" -f migrations/04_create_rls_policies.sql
psql "YOUR_SUPABASE_CONNECTION_STRING" -f migrations/05_create_functions.sql
```

### Step 2: Verify Installation

```sql
-- Check tables (should return 15)
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS is enabled (all should be true)
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public';

-- Check functions (should return 15+)
SELECT COUNT(*) FROM information_schema.routines 
WHERE routine_schema = 'public';
```

### Step 3: Configure Application

Update your `.env`:

```env
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
DATABASE_URL=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 🔐 Security Features

### Row Level Security (RLS)

All tables have RLS enabled with organization-based isolation:

- **Organization Isolation:** Users can only access data within their organization
- **Role-Based Access:** Different permissions for buyer, approver, admin, vendor roles
- **Superuser Override:** Superusers can access all data across organizations

### Key Security Policies

```sql
-- Users can only view their organization's data
CREATE POLICY "Users can view requests in their organization"
ON requests FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM user_accounts 
        WHERE user_accounts.id = requests.user_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
);

-- Audit logs are immutable
CREATE TRIGGER trigger_audit_logs_prevent_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_log_modification();
```

## ⚡ Performance Optimizations

### Indexes

- **Primary Keys:** Auto-incrementing integers on all tables
- **Unique Indexes:** Email, username, external IDs
- **Foreign Keys:** Automatic indexes on all relationships
- **Query Indexes:** Status fields, timestamps, categories
- **JSONB Indexes:** GIN indexes for JSON column searches
- **Text Search:** Trigram indexes for vendor name search

### Connection Pooling

```python
# Transaction Mode (Port 6543) - For API/Serverless
DATABASE_URL = "postgresql://...pooler.supabase.com:6543/postgres"

# Session Mode (Port 5432) - For Long-Running Workers
DATABASE_URL_SESSION = "postgresql://...pooler.supabase.com:5432/postgres"
```

## 🛠️ Helper Functions

### Analytics Functions

```sql
-- Get organization metrics
SELECT * FROM get_organization_metrics('your-org-id');

-- Get negotiation analytics
SELECT * FROM get_negotiation_analytics('session-123');

-- Get expiring contracts
SELECT * FROM get_expiring_contracts('your-org-id', 90);

-- Search vendors
SELECT * FROM search_vendors('salesforce', 'crm', 4.0);
```

### Maintenance Functions

```sql
-- Clean up expired sessions
SELECT cleanup_expired_sessions();

-- Archive old negotiations (older than 365 days)
SELECT archive_old_sessions(365);
```

## 📈 Real-Time Subscriptions

Enable real-time updates for live negotiation tracking:

```sql
-- Enable real-time on key tables
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_events;
ALTER PUBLICATION supabase_realtime ADD TABLE offers;
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_sessions;
```

```python
# Subscribe to events in Python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def handle_event(payload):
    print(f"New negotiation event: {payload}")

supabase.table("negotiation_events").on("INSERT", handle_event).subscribe()
```

## 🔄 Automatic Triggers

### Timestamp Management

All tables automatically update `updated_at` on modification:

```sql
CREATE TRIGGER trigger_requests_updated_at
BEFORE UPDATE ON requests
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

### Business Logic Triggers

- **Contract Validation:** Ensures end_date > start_date
- **Total Value Calculation:** Auto-calculates contract total_value
- **Negotiation Tracking:** Increments message count on new offers
- **Login Tracking:** Updates last_login_at on successful authentication
- **Audit Protection:** Prevents modification of audit logs

## 📝 Data Model Relationships

```
organizations
    ↓
user_accounts
    ↓
requests → negotiation_sessions → offers → contracts
              ↓                      ↓
         negotiation_events    audit_logs
    
vendor_profiles → offers → contracts
```

## 🧪 Testing

### Seed Test Data

```sql
-- Create test organization
INSERT INTO organizations (organization_id, name, plan, is_active)
VALUES ('test-org', 'Test Organization', 'pro', true);

-- Create test user
INSERT INTO user_accounts (
    email, username, hashed_password, full_name, 
    role, organization_id, is_active, email_verified
)
VALUES (
    'test@test-org.com', 'testuser', 
    '$2b$12$...', 'Test User',
    'buyer', 'test-org', true, true
);
```

### Verify RLS Policies

```sql
-- Set user context (simulates authenticated user)
SET LOCAL role TO authenticated;
SET LOCAL request.jwt.claims TO '{"sub": "1"}';

-- Test data access (should only see own org's data)
SELECT * FROM requests;
```

## 📚 Documentation

- **Migration Plan:** `../SUPABASE_MIGRATION_PLAN.md`
- **Setup Guide:** `../SUPABASE_SETUP_GUIDE.md`
- **Architecture:** `../docs/architecture.md`
- **Database Schema:** `../DATABASE_README.md`

## 🐛 Troubleshooting

### Common Issues

**1. Permission Denied**
```sql
-- Check RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
```

**2. Connection Pool Exhausted**
```python
# Use transaction mode pooler (port 6543)
# Increase pool size
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=40)
```

**3. Slow Queries**
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM requests WHERE status = 'pending';

-- Update table statistics
ANALYZE requests;
```

## 🔧 Maintenance

### Regular Tasks

```sql
-- Daily: Clean expired sessions
SELECT cleanup_expired_sessions();

-- Weekly: Update statistics
ANALYZE;

-- Monthly: Archive old data
SELECT archive_old_sessions(365);

-- Quarterly: Check database size
SELECT pg_size_pretty(pg_database_size('postgres'));
```

### Backup Strategy

Supabase provides automatic daily backups. For manual backups:

```bash
# Export schema
pg_dump -h db.xxx.supabase.co -U postgres --schema-only postgres > schema.sql

# Export data
pg_dump -h db.xxx.supabase.co -U postgres --data-only postgres > data.sql
```

## 📊 Monitoring

### Key Metrics to Monitor

1. **Database Size:** Should grow predictably
2. **Connection Count:** Should stay below pool limits
3. **Query Performance:** Monitor slow queries
4. **RLS Policy Performance:** Ensure policies are efficient
5. **Index Usage:** Verify indexes are being used

### Monitoring Queries

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('postgres'));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 🚨 Emergency Procedures

### Rollback

```sql
-- Disable RLS temporarily (emergency only)
ALTER TABLE requests DISABLE ROW LEVEL SECURITY;

-- Drop all tables (DESTRUCTIVE - use with caution)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

### Recovery

```bash
# Restore from backup
psql "YOUR_CONNECTION_STRING" < backup.sql
```

## 📞 Support

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Supabase Discord:** https://discord.supabase.com

## 📄 License

Part of the Procur procurement automation platform.

---

**Version:** 1.0  
**Last Updated:** 2025-10-07  
**Database Version:** PostgreSQL 15+  
**Supabase Project:** procur (uedvyexzjlovliiaawuc)
