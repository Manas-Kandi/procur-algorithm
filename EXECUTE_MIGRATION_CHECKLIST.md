# Supabase Migration Execution Checklist

## ✅ Pre-Migration Checklist

- [ ] Supabase account created
- [ ] Project "procur" exists (ID: `uedvyexzjlovliiaawuc`)
- [ ] You have admin access to the project
- [ ] All migration files are available in `supabase/migrations/`

---

## 🚀 Migration Execution Steps

### Step 1: Access Supabase Dashboard (2 minutes)

1. Go to: https://app.supabase.com
2. Log in to your account
3. Select project: **procur**
4. Navigate to: **SQL Editor** (left sidebar)

**Status:** [ ] Complete

---

### Step 2: Execute Migration Scripts (10 minutes)

Execute each script **in order** by clicking **New Query**, pasting the content, and clicking **Run**.

#### Script 1: Create Tables
- [ ] Open file: `supabase/migrations/01_create_tables.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: "Success. No rows returned" or similar
- [ ] Expected: 15 tables created

#### Script 2: Create Indexes
- [ ] Open file: `supabase/migrations/02_create_indexes.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: Success message
- [ ] Expected: 50+ indexes created

#### Script 3: Create Triggers
- [ ] Open file: `supabase/migrations/03_create_triggers.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: Success message
- [ ] Expected: 20+ triggers created

#### Script 4: Create RLS Policies
- [ ] Open file: `supabase/migrations/04_create_rls_policies.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: Success message
- [ ] Expected: 60+ RLS policies created

#### Script 5: Create Helper Functions
- [ ] Open file: `supabase/migrations/05_create_functions.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: Success message
- [ ] Expected: 15+ functions created

#### Script 6: Seed Sample Data (OPTIONAL)
- [ ] Open file: `supabase/migrations/06_seed_sample_data.sql`
- [ ] Copy entire contents
- [ ] Paste in SQL Editor
- [ ] Click **Run**
- [ ] Verify: Success message with counts
- [ ] Expected: Sample organizations, users, vendors, requests

**Status:** [ ] All scripts executed successfully

---

### Step 3: Verify Installation (5 minutes)

Run these verification queries in SQL Editor:

#### Verify Tables
```sql
-- Should return 15
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';
```
- [ ] Result: 15 tables
- [ ] **Actual count:** _______

#### Verify RLS Enabled
```sql
-- All should be true
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
```
- [ ] All tables show `rowsecurity = true`

#### Verify Indexes
```sql
-- Should return 50+
SELECT COUNT(*) as index_count
FROM pg_indexes 
WHERE schemaname = 'public';
```
- [ ] Result: 50+ indexes
- [ ] **Actual count:** _______

#### Verify Functions
```sql
-- Should return 15+
SELECT COUNT(*) as function_count
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION';
```
- [ ] Result: 15+ functions
- [ ] **Actual count:** _______

#### Verify Triggers
```sql
-- Should return 20+
SELECT COUNT(*) as trigger_count
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```
- [ ] Result: 20+ triggers
- [ ] **Actual count:** _______

**Status:** [ ] All verifications passed

---

### Step 4: Get API Keys (3 minutes)

1. Navigate to: **Settings** → **API** (in Supabase Dashboard)
2. Copy the following:

#### Project URL
```
https://uedvyexzjlovliiaawuc.supabase.co
```
- [ ] Copied

#### anon (public) key
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- [ ] Copied to `.env` file

#### service_role (secret) key
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- [ ] Copied to `.env` file
- [ ] ⚠️ **NEVER** commit this to version control

**Status:** [ ] API keys secured

---

### Step 5: Get Database Connection String (2 minutes)

1. Navigate to: **Settings** → **Database**
2. Scroll to: **Connection String**
3. Select: **URI**
4. Copy both connection strings:

#### Transaction Mode (Port 6543) - For API/Serverless
```
postgresql://postgres.uedvyexzjlovliiaawuc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```
- [ ] Copied to `.env` as `DATABASE_URL`

#### Session Mode (Port 5432) - For Workers
```
postgresql://postgres.uedvyexzjlovliiaawuc:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```
- [ ] Copied to `.env` as `DATABASE_URL_SESSION`

**Status:** [ ] Connection strings configured

---

### Step 6: Update Environment Variables (5 minutes)

Create or update `.env` file in project root:

```env
# Supabase Configuration
SUPABASE_URL=https://uedvyexzjlovliiaawuc.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Database Connection (Transaction Mode - for API)
DATABASE_URL=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Database Connection (Session Mode - for workers)
DATABASE_URL_SESSION=postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Legacy Procur DB Config (if needed for compatibility)
PROCUR_DB_HOST=aws-0-us-east-1.pooler.supabase.com
PROCUR_DB_PORT=6543
PROCUR_DB_DATABASE=postgres
PROCUR_DB_USERNAME=postgres.uedvyexzjlovliiaawuc
PROCUR_DB_PASSWORD=your_password_here
```

- [ ] `.env` file created/updated
- [ ] All values filled in
- [ ] `.env` added to `.gitignore`

**Status:** [ ] Environment configured

---

### Step 7: Test Connection (5 minutes)

#### Option A: Using Python Supabase Client

Create `test_supabase_connection.py`:

```python
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Test connection
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

try:
    # Test query
    result = supabase.table("organizations").select("*").execute()
    print(f"✅ Connection successful!")
    print(f"   Organizations found: {len(result.data)}")
    
    # Test function
    result = supabase.rpc("get_organization_metrics", {"org_id": "demo-org"}).execute()
    print(f"✅ Functions working!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run:
```bash
python test_supabase_connection.py
```

- [ ] Connection test passed
- [ ] Functions test passed

#### Option B: Using psql

```bash
psql "postgresql://postgres.uedvyexzjlovliiaawuc:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres" -c "SELECT COUNT(*) FROM organizations;"
```

- [ ] psql connection successful

**Status:** [ ] Connection verified

---

### Step 8: Enable Real-Time (Optional, 2 minutes)

If you want live negotiation updates:

```sql
-- Enable real-time on key tables
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_events;
ALTER PUBLICATION supabase_realtime ADD TABLE offers;
ALTER PUBLICATION supabase_realtime ADD TABLE negotiation_sessions;
```

- [ ] Real-time enabled (if needed)

**Status:** [ ] Real-time configured (or skipped)

---

### Step 9: Create Storage Bucket (Optional, 3 minutes)

For contract document storage:

1. Navigate to: **Storage** in Supabase Dashboard
2. Click: **New Bucket**
3. Name: `contracts`
4. Privacy: **Private**
5. Click: **Create Bucket**

Then add RLS policies (run in SQL Editor):

```sql
-- Allow users to upload contracts for their org
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

-- Allow users to view contracts for their org
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

- [ ] Storage bucket created (if needed)
- [ ] RLS policies added

**Status:** [ ] Storage configured (or skipped)

---

## 🎯 Post-Migration Checklist

### Database Verification
- [ ] 15 tables created
- [ ] 50+ indexes created
- [ ] 20+ triggers created
- [ ] 60+ RLS policies created
- [ ] 15+ functions created
- [ ] Sample data loaded (if script 6 was run)

### Configuration Verification
- [ ] API keys copied and secured
- [ ] Database connection strings configured
- [ ] `.env` file created and populated
- [ ] `.env` added to `.gitignore`

### Testing Verification
- [ ] Connection test passed
- [ ] Can query tables
- [ ] Functions work correctly
- [ ] RLS policies enforced

### Optional Features
- [ ] Real-time enabled (if needed)
- [ ] Storage bucket created (if needed)

---

## 📊 Migration Summary

**Execution Date:** _______________  
**Executed By:** _______________  
**Total Time:** _______________  

**Tables Created:** _______  
**Indexes Created:** _______  
**Functions Created:** _______  
**RLS Policies Created:** _______  

**Issues Encountered:** 
_______________________________________
_______________________________________
_______________________________________

**Resolution:** 
_______________________________________
_______________________________________
_______________________________________

---

## 🚨 Troubleshooting

### Issue: "permission denied for table X"
**Solution:** Ensure you're using `service_role` key for admin operations, or check RLS policies.

### Issue: "relation does not exist"
**Solution:** Verify script 1 (create tables) was executed successfully.

### Issue: "function does not exist"
**Solution:** Verify script 5 (create functions) was executed successfully.

### Issue: "connection pool exhausted"
**Solution:** Use transaction mode pooler (port 6543) or increase pool size in application.

### Issue: "syntax error in SQL"
**Solution:** Ensure you copied the entire file contents, including all lines.

---

## 📞 Support

**Documentation:**
- Setup Guide: `SUPABASE_SETUP_GUIDE.md`
- Quick Reference: `SUPABASE_QUICK_REFERENCE.md`
- Migration Plan: `SUPABASE_MIGRATION_PLAN.md`

**External Resources:**
- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

## ✅ Final Sign-Off

- [ ] All migration scripts executed successfully
- [ ] All verification tests passed
- [ ] Application can connect to database
- [ ] Team notified of migration completion
- [ ] Documentation updated

**Migration Status:** [ ] COMPLETE

**Signed:** _______________  
**Date:** _______________

---

**Next Steps:**
1. Update application code to use Supabase
2. Deploy to staging environment
3. Run integration tests
4. Deploy to production
5. Monitor performance and errors
