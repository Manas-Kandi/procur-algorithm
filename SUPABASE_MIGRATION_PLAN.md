# Supabase Migration Plan for Procur Platform

## Executive Summary

This document provides a comprehensive, end-to-end plan for migrating the Procur procurement negotiation platform to Supabase. The migration includes 14 core tables with complete schema definitions, Row Level Security (RLS) policies, indexes, triggers, and helper functions.

**Project Details:**
- **Supabase Project ID:** `uedvyexzjlovliiaawuc`
- **Project URL:** `https://uedvyexzjlovliiaawuc.supabase.co`
- **Database:** PostgreSQL 15+ (Supabase managed)
- **Total Tables:** 14
- **Total Indexes:** 35+
- **RLS Policies:** Multi-tenant with organization isolation

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Migration Strategy](#migration-strategy)
4. [Security Model](#security-model)
5. [Performance Optimization](#performance-optimization)
6. [Implementation Steps](#implementation-steps)
7. [Testing & Validation](#testing--validation)
8. [Rollback Plan](#rollback-plan)

---

## Architecture Overview

### Core Components

The Procur platform consists of the following data domains:

1. **Authentication & Authorization**
   - Organizations (multi-tenancy)
   - User Accounts
   - User Sessions
   - API Keys
   - OAuth Connections
   - Password History
   - Login Attempts

2. **Procurement Workflow**
   - Requests (procurement intents)
   - Vendor Profiles
   - Offers (negotiation proposals)
   - Contracts (finalized agreements)

3. **Negotiation Engine**
   - Negotiation Sessions
   - Negotiation Events (real-time streaming)

4. **Governance & Compliance**
   - Policy Configs
   - Audit Logs

### Data Flow

```
User → Request → Negotiation Session → Offers → Contract
                        ↓
                  Audit Logs
                  Negotiation Events
```

---

## Database Schema

### Table Summary

| Table | Purpose | Relationships | Special Features |
|-------|---------|---------------|------------------|
| `organizations` | Multi-tenant isolation | → user_accounts | Soft delete |
| `user_accounts` | Authentication | → requests, sessions, api_keys | MFA, password policy |
| `user_sessions` | Session management | user_accounts → | Token refresh |
| `api_keys` | Programmatic access | user_accounts → | Scoped permissions |
| `password_history` | Password reuse prevention | user_accounts → | Audit trail |
| `login_attempts` | Security monitoring | user_accounts → | Brute force detection |
| `oauth_connections` | SSO integration | user_accounts → | Provider tokens |
| `requests` | Procurement requests | user_accounts → offers, contracts | Structured intake |
| `vendor_profiles` | Vendor catalog | → offers, contracts | Data enrichment |
| `offers` | Negotiation proposals | requests, vendors → | Utility scoring |
| `contracts` | Finalized agreements | requests, vendors, offers → | E-signature, ERP sync |
| `negotiation_sessions` | Session tracking | requests, vendors → offers | Round management |
| `negotiation_events` | Real-time events | → (session_id) | Streaming support |
| `audit_logs` | Compliance audit | user_accounts, sessions → | Immutable |
| `policy_configs` | Policy engine | organizations → | Versioned |

---

## Migration Strategy

### Phase 1: Core Infrastructure (Tables 1-7)
**Duration:** 1 hour  
**Risk:** Low

1. Organizations
2. User Accounts
3. User Sessions
4. API Keys
5. Password History
6. Login Attempts
7. OAuth Connections

### Phase 2: Business Logic (Tables 8-12)
**Duration:** 1 hour  
**Risk:** Medium

8. Requests
9. Vendor Profiles
10. Offers
11. Contracts
12. Negotiation Sessions

### Phase 3: Operational (Tables 13-14)
**Duration:** 30 minutes  
**Risk:** Low

13. Negotiation Events
14. Audit Logs
15. Policy Configs

### Phase 4: Security & Performance
**Duration:** 1 hour  
**Risk:** Low

- Row Level Security policies
- Indexes
- Triggers
- Helper functions

---

## Security Model

### Row Level Security (RLS)

Supabase requires RLS policies for secure multi-tenant access. The Procur platform uses organization-based isolation.

#### Policy Strategy

1. **Organization Isolation**
   - Users can only access data within their organization
   - Superusers can access all organizations

2. **Role-Based Access**
   - `buyer`: Create requests, view offers
   - `approver`: Approve requests
   - `admin`: Manage organization settings
   - `vendor`: View assigned negotiations

3. **API Key Scoping**
   - API keys inherit user permissions
   - Additional scope restrictions apply

### Authentication Flow

```
User Login → Supabase Auth → JWT Token → RLS Policies → Data Access
```

---

## Performance Optimization

### Indexing Strategy

1. **Primary Keys:** All tables use auto-incrementing integers
2. **Unique Indexes:** Email, username, external IDs
3. **Foreign Key Indexes:** Automatic for relationships
4. **Query Indexes:** Status fields, timestamps, categories
5. **JSON Indexes:** GIN indexes for JSONB columns

### Connection Pooling

- **Supabase Pooler:** PgBouncer in transaction mode
- **Recommended Pool Size:** 20-40 connections
- **Max Client Connections:** 100

### Query Optimization

- Use `select` to limit columns
- Leverage Supabase's automatic query optimization
- Use materialized views for complex analytics

---

## Implementation Steps

### Step 1: Prepare Supabase Project

1. Log in to Supabase Dashboard: https://app.supabase.com
2. Navigate to your project: `procur`
3. Go to SQL Editor

### Step 2: Execute Migration Scripts

Execute the following SQL files in order:

1. `01_create_tables.sql` - Create all tables
2. `02_create_indexes.sql` - Add performance indexes
3. `03_create_triggers.sql` - Add timestamp triggers
4. `04_create_rls_policies.sql` - Enable Row Level Security
5. `05_create_functions.sql` - Helper functions

### Step 3: Configure Application

Update your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-role-key>

# Database Direct Connection (for migrations)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### Step 4: Migrate Data (if applicable)

If migrating from existing PostgreSQL:

```bash
# Export from old database
pg_dump -h localhost -U procur_user procur > procur_export.sql

# Import to Supabase (use connection string from Supabase dashboard)
psql "postgresql://postgres.[project-ref]:[password]@db.[project-ref].supabase.co:5432/postgres" < procur_export.sql
```

### Step 5: Verify Migration

Run validation queries:

```sql
-- Check table counts
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Verify indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check RLS policies
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'public';
```

---

## Testing & Validation

### Unit Tests

1. **Table Creation:** Verify all 14 tables exist
2. **Constraints:** Test foreign keys and unique constraints
3. **Triggers:** Verify timestamp updates
4. **RLS Policies:** Test multi-tenant isolation

### Integration Tests

1. **User Registration:** Create user and organization
2. **Request Creation:** Create procurement request
3. **Negotiation Flow:** Create session, offers, contract
4. **Audit Trail:** Verify all actions logged

### Performance Tests

1. **Query Performance:** < 100ms for simple queries
2. **Bulk Insert:** 1000 records/second
3. **Concurrent Users:** 100+ simultaneous connections

---

## Rollback Plan

### Emergency Rollback

If critical issues occur:

```sql
-- Disable RLS temporarily
ALTER TABLE user_accounts DISABLE ROW LEVEL SECURITY;
ALTER TABLE requests DISABLE ROW LEVEL SECURITY;
-- ... repeat for all tables

-- Drop all tables (DESTRUCTIVE)
DROP TABLE IF EXISTS negotiation_events CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS policy_configs CASCADE;
-- ... continue in reverse dependency order
```

### Backup Strategy

1. **Pre-Migration Backup:** Export current database
2. **Point-in-Time Recovery:** Supabase provides automatic backups
3. **Manual Snapshots:** Create before major changes

---

## Supabase-Specific Features

### Real-Time Subscriptions

Enable real-time for negotiation events:

```sql
-- Enable real-time on negotiation_events table
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_events;
```

### Storage Integration

For contract documents:

```sql
-- Create storage bucket for contracts
INSERT INTO storage.buckets (id, name, public)
VALUES ('contracts', 'contracts', false);

-- Add RLS policy for contract storage
CREATE POLICY "Users can access their org's contracts"
ON storage.objects FOR SELECT
USING (bucket_id = 'contracts' AND auth.uid() IN (
  SELECT id FROM user_accounts WHERE organization_id = (
    SELECT organization_id FROM user_accounts WHERE id = auth.uid()
  )
));
```

### Edge Functions

Deploy serverless functions for:
- Email notifications
- Webhook handlers
- Background jobs

---

## Connection Configuration

### Python (SQLAlchemy)

```python
from sqlalchemy import create_engine
import os

# Use Supabase connection pooler
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Python (Supabase Client)

```python
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Query with RLS
data = supabase.table("requests").select("*").execute()
```

---

## Monitoring & Observability

### Supabase Dashboard Metrics

Monitor:
- Database size and growth
- Query performance
- Connection pool usage
- API request rates

### Custom Metrics

```sql
-- Active negotiation sessions
CREATE VIEW active_negotiations AS
SELECT COUNT(*) as count, status
FROM negotiation_sessions
WHERE status = 'active'
GROUP BY status;

-- Request pipeline
CREATE VIEW request_pipeline AS
SELECT status, COUNT(*) as count, AVG(budget_max) as avg_budget
FROM requests
WHERE deleted_at IS NULL
GROUP BY status;
```

---

## Cost Optimization

### Supabase Pricing Tiers

- **Free Tier:** Up to 500MB database, 2GB bandwidth
- **Pro Tier ($25/mo):** 8GB database, 50GB bandwidth
- **Team/Enterprise:** Custom pricing

### Optimization Tips

1. **Use Connection Pooler:** Reduce connection overhead
2. **Implement Caching:** Redis for frequently accessed data
3. **Archive Old Data:** Move completed negotiations to cold storage
4. **Optimize Queries:** Use EXPLAIN ANALYZE for slow queries

---

## Next Steps

1. ✅ Review this migration plan
2. ⏳ Execute SQL scripts in Supabase SQL Editor
3. ⏳ Configure application environment variables
4. ⏳ Run validation tests
5. ⏳ Deploy application with Supabase backend
6. ⏳ Monitor performance and optimize

---

## Support Resources

- **Supabase Documentation:** https://supabase.com/docs
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Procur Architecture:** See `docs/architecture.md`
- **Database Schema:** See `src/procur/db/models.py`

---

## Appendix: Schema Diagram

```
┌─────────────────┐
│ organizations   │
└────────┬────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
┌────────▼────────┐                ┌───────▼──────┐
│ user_accounts   │◄───────────────┤ requests     │
└────┬────┬───┬───┘                └──────┬───────┘
     │    │   │                           │
     │    │   │                           │
     │    │   └──────────┐                │
     │    │              │                │
┌────▼────▼───┐   ┌──────▼──────┐  ┌─────▼────────┐
│ sessions    │   │ api_keys    │  │ offers       │
│ password_   │   │ oauth_conn  │  │              │
│ login_att   │   └─────────────┘  └──────┬───────┘
└─────────────┘                           │
                                          │
                    ┌─────────────────────┤
                    │                     │
            ┌───────▼────────┐   ┌────────▼─────────┐
            │ vendor_profiles│   │ negotiation_     │
            └───────┬────────┘   │ sessions         │
                    │            └──────────────────┘
                    │
            ┌───────▼────────┐
            │ contracts      │
            └────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-07  
**Author:** Procur Platform Team
