-- =====================================================
-- Drop all existing RLS policies and functions
-- Run this BEFORE running 04_create_rls_policies_fixed.sql
-- =====================================================

-- Drop all policies on organizations
DROP POLICY IF EXISTS "Users can view their organization" ON organizations;
DROP POLICY IF EXISTS "Superusers can insert organizations" ON organizations;
DROP POLICY IF EXISTS "Admins can update their organization" ON organizations;
DROP POLICY IF EXISTS "Superusers can delete organizations" ON organizations;

-- Drop all policies on user_accounts
DROP POLICY IF EXISTS "Users can view users in their organization" ON user_accounts;
DROP POLICY IF EXISTS "Admins can create users in their organization" ON user_accounts;
DROP POLICY IF EXISTS "Users can update their own account" ON user_accounts;
DROP POLICY IF EXISTS "Admins can delete users in their organization" ON user_accounts;

-- Drop all policies on user_sessions
DROP POLICY IF EXISTS "Users can view their own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can create their own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can update their own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can delete their own sessions" ON user_sessions;

-- Drop all policies on api_keys
DROP POLICY IF EXISTS "Users can view their own API keys" ON api_keys;
DROP POLICY IF EXISTS "Users can create their own API keys" ON api_keys;
DROP POLICY IF EXISTS "Users can update their own API keys" ON api_keys;
DROP POLICY IF EXISTS "Users can delete their own API keys" ON api_keys;

-- Drop all policies on password_history
DROP POLICY IF EXISTS "Users can view their own password history" ON password_history;
DROP POLICY IF EXISTS "System can insert password history" ON password_history;

-- Drop all policies on login_attempts
DROP POLICY IF EXISTS "Users can view their own login attempts" ON login_attempts;
DROP POLICY IF EXISTS "System can insert login attempts" ON login_attempts;

-- Drop all policies on oauth_connections
DROP POLICY IF EXISTS "Users can view their own OAuth connections" ON oauth_connections;
DROP POLICY IF EXISTS "Users can create their own OAuth connections" ON oauth_connections;
DROP POLICY IF EXISTS "Users can update their own OAuth connections" ON oauth_connections;
DROP POLICY IF EXISTS "Users can delete their own OAuth connections" ON oauth_connections;

-- Drop all policies on requests
DROP POLICY IF EXISTS "Users can view requests in their organization" ON requests;
DROP POLICY IF EXISTS "Users can create their own requests" ON requests;
DROP POLICY IF EXISTS "Users can update their own requests" ON requests;
DROP POLICY IF EXISTS "Users can delete their own requests" ON requests;

-- Drop all policies on vendor_profiles
DROP POLICY IF EXISTS "Authenticated users can view vendor profiles" ON vendor_profiles;
DROP POLICY IF EXISTS "Admins can create vendor profiles" ON vendor_profiles;
DROP POLICY IF EXISTS "Admins can update vendor profiles" ON vendor_profiles;
DROP POLICY IF EXISTS "Superusers can delete vendor profiles" ON vendor_profiles;

-- Drop all policies on negotiation_sessions
DROP POLICY IF EXISTS "Users can view negotiation sessions in their organization" ON negotiation_sessions;
DROP POLICY IF EXISTS "System can create negotiation sessions" ON negotiation_sessions;
DROP POLICY IF EXISTS "System can update negotiation sessions" ON negotiation_sessions;

-- Drop all policies on offers
DROP POLICY IF EXISTS "Users can view offers in their organization" ON offers;
DROP POLICY IF EXISTS "System can create offers" ON offers;
DROP POLICY IF EXISTS "System can update offers" ON offers;

-- Drop all policies on contracts
DROP POLICY IF EXISTS "Users can view contracts in their organization" ON contracts;
DROP POLICY IF EXISTS "Authorized users can create contracts" ON contracts;
DROP POLICY IF EXISTS "Authorized users can update contracts" ON contracts;

-- Drop all policies on negotiation_events
DROP POLICY IF EXISTS "Users can view negotiation events in their organization" ON negotiation_events;
DROP POLICY IF EXISTS "System can insert negotiation events" ON negotiation_events;

-- Drop all policies on audit_logs
DROP POLICY IF EXISTS "Users can view audit logs in their organization" ON audit_logs;
DROP POLICY IF EXISTS "System can insert audit logs" ON audit_logs;

-- Drop all policies on policy_configs
DROP POLICY IF EXISTS "Users can view policies in their organization" ON policy_configs;
DROP POLICY IF EXISTS "Admins can create policies for their organization" ON policy_configs;
DROP POLICY IF EXISTS "Admins can update policies for their organization" ON policy_configs;
DROP POLICY IF EXISTS "Admins can delete policies for their organization" ON policy_configs;

-- Drop existing helper functions
DROP FUNCTION IF EXISTS get_current_user_id();
DROP FUNCTION IF EXISTS get_user_organization_id();
DROP FUNCTION IF EXISTS is_superuser();
DROP FUNCTION IF EXISTS has_role(VARCHAR);
DROP FUNCTION IF EXISTS has_role(TEXT);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'All existing RLS policies and functions have been dropped.';
    RAISE NOTICE 'Now run 04_create_rls_policies_fixed.sql';
END $$;
