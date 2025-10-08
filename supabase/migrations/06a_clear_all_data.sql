-- =====================================================
-- CLEAR ALL DATA - Run this before 06_seed_sample_data.sql
-- =====================================================

-- Disable triggers temporarily to avoid cascade issues
SET session_replication_role = replica;

-- Delete in reverse dependency order
TRUNCATE TABLE negotiation_events CASCADE;
TRUNCATE TABLE audit_logs CASCADE;
TRUNCATE TABLE policy_configs CASCADE;
TRUNCATE TABLE offers CASCADE;
TRUNCATE TABLE contracts CASCADE;
TRUNCATE TABLE negotiation_sessions CASCADE;
TRUNCATE TABLE requests CASCADE;
TRUNCATE TABLE vendor_profiles CASCADE;
TRUNCATE TABLE oauth_connections CASCADE;
TRUNCATE TABLE login_attempts CASCADE;
TRUNCATE TABLE password_history CASCADE;
TRUNCATE TABLE api_keys CASCADE;
TRUNCATE TABLE user_sessions CASCADE;
TRUNCATE TABLE user_accounts CASCADE;
TRUNCATE TABLE organizations CASCADE;

-- Re-enable triggers
SET session_replication_role = DEFAULT;

SELECT 'All data cleared successfully' AS status;
