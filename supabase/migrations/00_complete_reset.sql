-- =====================================================
-- COMPLETE DATABASE RESET
-- WARNING: This will delete ALL data and recreate tables
-- =====================================================

-- Drop all tables in correct order
DROP TABLE IF EXISTS negotiation_events CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS policy_configs CASCADE;
DROP TABLE IF EXISTS offers CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS negotiation_sessions CASCADE;
DROP TABLE IF EXISTS requests CASCADE;
DROP TABLE IF EXISTS vendor_profiles CASCADE;
DROP TABLE IF EXISTS oauth_connections CASCADE;
DROP TABLE IF EXISTS login_attempts CASCADE;
DROP TABLE IF EXISTS password_history CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_accounts CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

SELECT 'All tables dropped. Now run scripts 01-06 in order.' AS status;
