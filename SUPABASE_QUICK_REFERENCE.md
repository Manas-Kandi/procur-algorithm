# Supabase Quick Reference - Procur Platform

## 🎯 Your Project Details

- **Project ID:** `uedvyexzjlovliiaawuc`
- **Project URL:** `https://uedvyexzjlovliiaawuc.supabase.co`
- **Dashboard:** [https://app.supabase.com/project/uedvyexzjlovliiaawuc](https://app.supabase.com/project/uedvyexzjlovliiaawuc)

---

## ⚡ 5-Minute Setup

### 1. Execute SQL Scripts (in Supabase SQL Editor)

Go to: **SQL Editor** → **New Query** → Copy/Paste → **Run**

```
✅ supabase/migrations/01_create_tables.sql      (15 tables)
✅ supabase/migrations/02_create_indexes.sql     (50+ indexes)
✅ supabase/migrations/03_create_triggers.sql    (20+ triggers)
✅ supabase/migrations/04_create_rls_policies.sql (60+ policies)
✅ supabase/migrations/05_create_functions.sql   (15+ functions)
```

### 2. Get Your API Keys

Go to: **Settings** → **API**

```env
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=<copy from dashboard>
SUPABASE_SERVICE_KEY=<copy from dashboard>
```

### 3. Get Database Connection String

Go to: **Settings** → **Database** → **Connection String** → **URI**

```env
# Transaction Mode (for API/serverless)
DATABASE_URL=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Session Mode (for workers)
DATABASE_URL_SESSION=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### 4. Verify Installation

```sql
-- Should return 15
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';

-- All should be true
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
```

---

## 📊 Database Schema Summary

### 15 Tables Created

| Category | Tables | Purpose |
|----------|--------|---------|
| **Auth** | organizations, user_accounts, user_sessions, api_keys, password_history, login_attempts, oauth_connections | Multi-tenant authentication with MFA |
| **Business** | requests, vendor_profiles, offers, contracts, negotiation_sessions | Core procurement workflow |
| **Operational** | negotiation_events, audit_logs, policy_configs | Real-time events, compliance, governance |

### Key Features

- ✅ **Multi-tenant:** Organization-based data isolation
- ✅ **Row Level Security:** 60+ RLS policies for secure access
- ✅ **Soft Deletes:** All core tables support soft deletion
- ✅ **Audit Trail:** Immutable audit logs for compliance
- ✅ **Real-time:** Support for live negotiation updates
- ✅ **Performance:** 50+ indexes for fast queries
- ✅ **Automation:** 20+ triggers for business logic

---

## 🔌 Connection Examples

### Python - Supabase Client

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Query data
requests = supabase.table("requests").select("*").eq("status", "pending").execute()

# Insert data
new_request = supabase.table("requests").insert({
    "request_id": "req-001",
    "user_id": 1,
    "description": "Need CRM",
    "request_type": "saas",
    "status": "pending"
}).execute()
```

### Python - SQLAlchemy

```python
from sqlalchemy import create_engine
import os

engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Use with your existing Procur models
from procur.db import get_session

with get_session() as session:
    # Your existing code works as-is
    pass
```

---

## 🔐 Security Model

### Organization Isolation

```
User A (Org: acme-corp) → Can only see acme-corp data
User B (Org: demo-org)  → Can only see demo-org data
Superuser              → Can see all data
```

### Role Permissions

| Role | Permissions |
|------|-------------|
| **buyer** | Create requests, view offers |
| **approver** | Approve requests |
| **admin** | Manage organization, users, policies |
| **vendor** | View assigned negotiations |
| **superuser** | Full access across all organizations |

---

## 📈 Useful Queries

### Analytics

```sql
-- Organization dashboard
SELECT * FROM get_organization_metrics('your-org-id');

-- Negotiation analytics
SELECT * FROM get_negotiation_analytics('session-123');

-- Expiring contracts (next 90 days)
SELECT * FROM get_expiring_contracts('your-org-id', 90);

-- Top vendors by savings
SELECT * FROM get_top_vendors_by_savings('your-org-id', 10);
```

### Monitoring

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('postgres'));

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
```

### Maintenance

```sql
-- Clean expired sessions (run daily)
SELECT cleanup_expired_sessions();

-- Archive old negotiations (run monthly)
SELECT archive_old_sessions(365);

-- Update statistics (run weekly)
ANALYZE;
```

---

## 🚀 Real-Time Setup

### Enable Real-Time

```sql
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_events;
ALTER PUBLICATION supabase_realtime ADD TABLE offers;
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_sessions;
```

### Subscribe in Python

```python
def handle_event(payload):
    print(f"New event: {payload}")

supabase.table("negotiation_events").on("INSERT", handle_event).subscribe()
```

---

## 🗂️ Storage Setup (Optional)

### Create Contract Storage Bucket

1. Go to **Storage** in dashboard
2. Create bucket: `contracts` (Private)
3. Add RLS policies (see SUPABASE_SETUP_GUIDE.md)

### Upload Contract

```python
with open("contract.pdf", "rb") as f:
    supabase.storage.from_("contracts").upload(
        f"org-123/contract-456.pdf",
        f,
        {"content-type": "application/pdf"}
    )
```

---

## 🧪 Test Data

### Create Test Organization & User

```sql
-- Organization
INSERT INTO organizations (organization_id, name, plan, is_active)
VALUES ('test-org', 'Test Organization', 'pro', true);

-- User (hash password with bcrypt first)
INSERT INTO user_accounts (
    email, username, hashed_password, full_name,
    role, organization_id, is_active, email_verified
) VALUES (
    'admin@test-org.com', 'admin',
    '$2b$12$...', 'Admin User',
    'admin', 'test-org', true, true
);
```

---

## 📱 Environment Variables Template

```env
# Supabase
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (Transaction Mode - for API)
DATABASE_URL=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Database (Session Mode - for workers)
DATABASE_URL_SESSION=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Legacy Procur DB Config (if needed)
PROCUR_DB_HOST=aws-0-us-east-1.pooler.supabase.com
PROCUR_DB_PORT=6543
PROCUR_DB_DATABASE=postgres
PROCUR_DB_USERNAME=postgres.uedvyexzjlovliiaawuc
PROCUR_DB_PASSWORD=[your-password]
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Check RLS policies, use service_role key for admin |
| Connection pool exhausted | Use transaction mode (port 6543), increase pool_size |
| Slow queries | Check indexes with `EXPLAIN ANALYZE`, run `ANALYZE` |
| Function not found | Re-run `05_create_functions.sql` |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `SUPABASE_MIGRATION_PLAN.md` | Comprehensive migration strategy |
| `SUPABASE_SETUP_GUIDE.md` | Step-by-step setup instructions |
| `supabase/README.md` | Technical reference for migrations |
| `supabase/migrations/*.sql` | SQL migration scripts |

---

## ✅ Post-Migration Checklist

- [ ] All 5 SQL scripts executed successfully
- [ ] 15 tables created
- [ ] RLS enabled on all tables
- [ ] API keys copied to `.env`
- [ ] Database connection string configured
- [ ] Test query executed successfully
- [ ] Application connected to Supabase
- [ ] Real-time enabled (if needed)
- [ ] Storage bucket created (if needed)
- [ ] Test data seeded
- [ ] Monitoring configured

---

## 🎓 Learning Resources

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Tutorial:** https://www.postgresql.org/docs/tutorial/
- **RLS Guide:** https://supabase.com/docs/guides/auth/row-level-security
- **Real-time Guide:** https://supabase.com/docs/guides/realtime

---

## 💡 Pro Tips

1. **Use Transaction Mode** (port 6543) for API/serverless functions
2. **Use Session Mode** (port 5432) for long-running workers
3. **Always use environment variables** for credentials
4. **Monitor connection pool usage** in Supabase dashboard
5. **Run `ANALYZE`** weekly to update query planner statistics
6. **Set up alerts** for database size and connection limits
7. **Test RLS policies** thoroughly before production
8. **Use `service_role` key** only on backend, never in client code

---

**Need Help?** Check the detailed guides:
- Setup: `SUPABASE_SETUP_GUIDE.md`
- Planning: `SUPABASE_MIGRATION_PLAN.md`
- Technical: `supabase/README.md`
