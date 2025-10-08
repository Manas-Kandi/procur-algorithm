-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 04_create_rls_policies.sql
-- Description: Row Level Security (RLS) policies for multi-tenant access control
-- =====================================================

-- =====================================================
-- ENABLE RLS ON ALL TABLES
-- =====================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE negotiation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE negotiation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_configs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- HELPER FUNCTION: get_current_user_id
-- Get the current user's integer ID from auth.uid()
-- Note: Supabase auth.uid() returns UUID, but our tables use INTEGER
-- We'll store a mapping or use email as the bridge
-- =====================================================

CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS INTEGER AS $$
DECLARE
    user_email TEXT;
    user_id INTEGER;
BEGIN
    -- Get email from JWT
    user_email := auth.jwt()->>'email';
    
    -- Return NULL if no email
    IF user_email IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Look up user by email
    SELECT id INTO user_id
    FROM user_accounts 
    WHERE email = user_email
    LIMIT 1;
    
    RETURN user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION get_current_user_id() IS 'Get current user integer ID from auth context';

-- =====================================================
-- HELPER FUNCTION: get_user_organization_id
-- Get the organization_id for the current authenticated user
-- =====================================================

CREATE OR REPLACE FUNCTION get_user_organization_id()
RETURNS VARCHAR(100) AS $$
DECLARE
    current_user_id INTEGER;
    org_id VARCHAR(100);
BEGIN
    current_user_id := get_current_user_id();
    
    IF current_user_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    SELECT organization_id INTO org_id
    FROM user_accounts 
    WHERE id = current_user_id;
    
    RETURN org_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION get_user_organization_id() IS 'Get organization_id for current authenticated user';

-- =====================================================
-- HELPER FUNCTION: is_superuser
-- Check if current user is a superuser
-- =====================================================

CREATE OR REPLACE FUNCTION is_superuser()
RETURNS BOOLEAN AS $$
DECLARE
    current_user_id INTEGER;
    is_super BOOLEAN;
BEGIN
    current_user_id := get_current_user_id();
    
    IF current_user_id IS NULL THEN
        RETURN false;
    END IF;
    
    SELECT user_accounts.is_superuser INTO is_super
    FROM user_accounts 
    WHERE id = current_user_id;
    
    RETURN COALESCE(is_super, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION is_superuser() IS 'Check if current user is a superuser';

-- =====================================================
-- HELPER FUNCTION: has_role
-- Check if current user has a specific role
-- =====================================================

CREATE OR REPLACE FUNCTION has_role(required_role VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    current_user_id INTEGER;
    user_role VARCHAR(50);
    is_super BOOLEAN;
BEGIN
    current_user_id := get_current_user_id();
    
    IF current_user_id IS NULL THEN
        RETURN false;
    END IF;
    
    SELECT role, is_superuser INTO user_role, is_super
    FROM user_accounts 
    WHERE id = current_user_id;
    
    RETURN COALESCE(user_role = required_role OR is_super = true, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION has_role(VARCHAR) IS 'Check if current user has a specific role';

-- =====================================================
-- RLS POLICIES: organizations
-- =====================================================

-- Users can view their own organization
CREATE POLICY "Users can view their organization"
ON organizations FOR SELECT
USING (
    organization_id = get_user_organization_id()
    OR is_superuser()
);

-- Only superusers can insert organizations
CREATE POLICY "Superusers can insert organizations"
ON organizations FOR INSERT
WITH CHECK (is_superuser());

-- Admins can update their organization
CREATE POLICY "Admins can update their organization"
ON organizations FOR UPDATE
USING (
    organization_id = get_user_organization_id()
    AND has_role('admin')
)
WITH CHECK (
    organization_id = get_user_organization_id()
    AND has_role('admin')
);

-- Only superusers can delete organizations
CREATE POLICY "Superusers can delete organizations"
ON organizations FOR DELETE
USING (is_superuser());

-- =====================================================
-- RLS POLICIES: user_accounts
-- =====================================================

-- Users can view users in their organization
CREATE POLICY "Users can view users in their organization"
ON user_accounts FOR SELECT
USING (
    organization_id = get_user_organization_id()
    OR is_superuser()
    OR id = get_current_user_id()
);

-- Admins can create users in their organization
CREATE POLICY "Admins can create users in their organization"
ON user_accounts FOR INSERT
WITH CHECK (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- Users can update their own account, admins can update their org
CREATE POLICY "Users can update their own account"
ON user_accounts FOR UPDATE
USING (
    id = get_current_user_id()
    OR (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
)
WITH CHECK (
    id = get_current_user_id()
    OR (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- Admins can soft delete users in their organization
CREATE POLICY "Admins can delete users in their organization"
ON user_accounts FOR DELETE
USING (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- =====================================================
-- RLS POLICIES: user_sessions
-- =====================================================

-- Users can view their own sessions
CREATE POLICY "Users can view their own sessions"
ON user_sessions FOR SELECT
USING (user_id = get_current_user_id() OR is_superuser());

-- Users can create their own sessions
CREATE POLICY "Users can create their own sessions"
ON user_sessions FOR INSERT
WITH CHECK (user_id = get_current_user_id());

-- Users can update their own sessions
CREATE POLICY "Users can update their own sessions"
ON user_sessions FOR UPDATE
USING (user_id = get_current_user_id() OR is_superuser())
WITH CHECK (user_id = get_current_user_id() OR is_superuser());

-- Users can delete their own sessions
CREATE POLICY "Users can delete their own sessions"
ON user_sessions FOR DELETE
USING (user_id = get_current_user_id() OR is_superuser());

-- =====================================================
-- RLS POLICIES: api_keys
-- =====================================================

-- Users can view their own API keys
CREATE POLICY "Users can view their own API keys"
ON api_keys FOR SELECT
USING (user_id = get_current_user_id() OR is_superuser());

-- Users can create their own API keys
CREATE POLICY "Users can create their own API keys"
ON api_keys FOR INSERT
WITH CHECK (user_id = get_current_user_id());

-- Users can update their own API keys
CREATE POLICY "Users can update their own API keys"
ON api_keys FOR UPDATE
USING (user_id = get_current_user_id() OR is_superuser())
WITH CHECK (user_id = get_current_user_id() OR is_superuser());

-- Users can delete their own API keys
CREATE POLICY "Users can delete their own API keys"
ON api_keys FOR DELETE
USING (user_id = get_current_user_id() OR is_superuser());

-- =====================================================
-- RLS POLICIES: password_history
-- =====================================================

-- Users can view their own password history
CREATE POLICY "Users can view their own password history"
ON password_history FOR SELECT
USING (user_id = get_current_user_id() OR is_superuser());

-- System can insert password history
CREATE POLICY "System can insert password history"
ON password_history FOR INSERT
WITH CHECK (user_id = get_current_user_id() OR is_superuser());

-- No updates or deletes allowed on password history
-- (Enforced by table design - no policies needed)

-- =====================================================
-- RLS POLICIES: login_attempts
-- =====================================================

-- Users can view their own login attempts
CREATE POLICY "Users can view their own login attempts"
ON login_attempts FOR SELECT
USING (user_id = get_current_user_id() OR is_superuser());

-- System can insert login attempts (no auth required for failed logins)
CREATE POLICY "System can insert login attempts"
ON login_attempts FOR INSERT
WITH CHECK (true);

-- =====================================================
-- RLS POLICIES: oauth_connections
-- =====================================================

-- Users can view their own OAuth connections
CREATE POLICY "Users can view their own OAuth connections"
ON oauth_connections FOR SELECT
USING (user_id = get_current_user_id() OR is_superuser());

-- Users can create their own OAuth connections
CREATE POLICY "Users can create their own OAuth connections"
ON oauth_connections FOR INSERT
WITH CHECK (user_id = get_current_user_id());

-- Users can update their own OAuth connections
CREATE POLICY "Users can update their own OAuth connections"
ON oauth_connections FOR UPDATE
USING (user_id = get_current_user_id() OR is_superuser())
WITH CHECK (user_id = get_current_user_id() OR is_superuser());

-- Users can delete their own OAuth connections
CREATE POLICY "Users can delete their own OAuth connections"
ON oauth_connections FOR DELETE
USING (user_id = get_current_user_id() OR is_superuser());

-- =====================================================
-- RLS POLICIES: requests
-- =====================================================

-- Users can view requests in their organization
CREATE POLICY "Users can view requests in their organization"
ON requests FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM user_accounts 
        WHERE user_accounts.id = requests.user_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- Users can create their own requests
CREATE POLICY "Users can create their own requests"
ON requests FOR INSERT
WITH CHECK (user_id = get_current_user_id());

-- Users can update their own requests, approvers can approve
CREATE POLICY "Users can update their own requests"
ON requests FOR UPDATE
USING (
    user_id = get_current_user_id()
    OR has_role('approver')
    OR has_role('admin')
    OR is_superuser()
)
WITH CHECK (
    user_id = get_current_user_id()
    OR has_role('approver')
    OR has_role('admin')
    OR is_superuser()
);

-- Users can delete their own requests
CREATE POLICY "Users can delete their own requests"
ON requests FOR DELETE
USING (
    user_id = get_current_user_id()
    OR has_role('admin')
    OR is_superuser()
);

-- =====================================================
-- RLS POLICIES: vendor_profiles
-- =====================================================

-- All authenticated users can view vendor profiles
CREATE POLICY "Authenticated users can view vendor profiles"
ON vendor_profiles FOR SELECT
USING (get_current_user_id() IS NOT NULL);

-- Only admins and superusers can create vendor profiles
CREATE POLICY "Admins can create vendor profiles"
ON vendor_profiles FOR INSERT
WITH CHECK (has_role('admin') OR is_superuser());

-- Only admins and superusers can update vendor profiles
CREATE POLICY "Admins can update vendor profiles"
ON vendor_profiles FOR UPDATE
USING (has_role('admin') OR is_superuser())
WITH CHECK (has_role('admin') OR is_superuser());

-- Only superusers can delete vendor profiles
CREATE POLICY "Superusers can delete vendor profiles"
ON vendor_profiles FOR DELETE
USING (is_superuser());

-- =====================================================
-- RLS POLICIES: negotiation_sessions
-- =====================================================

-- Users can view negotiation sessions for their organization's requests
CREATE POLICY "Users can view negotiation sessions in their organization"
ON negotiation_sessions FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE negotiation_sessions.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can create negotiation sessions
CREATE POLICY "System can create negotiation sessions"
ON negotiation_sessions FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE requests.id = request_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can update negotiation sessions
CREATE POLICY "System can update negotiation sessions"
ON negotiation_sessions FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE negotiation_sessions.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE negotiation_sessions.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- =====================================================
-- RLS POLICIES: offers
-- =====================================================

-- Users can view offers for their organization's requests
CREATE POLICY "Users can view offers in their organization"
ON offers FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE offers.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can create offers
CREATE POLICY "System can create offers"
ON offers FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE requests.id = request_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can update offers
CREATE POLICY "System can update offers"
ON offers FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE offers.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE offers.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- =====================================================
-- RLS POLICIES: contracts
-- =====================================================

-- Users can view contracts for their organization's requests
CREATE POLICY "Users can view contracts in their organization"
ON contracts FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE contracts.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- Authorized users can create contracts
CREATE POLICY "Authorized users can create contracts"
ON contracts FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE requests.id = request_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- Authorized users can update contracts
CREATE POLICY "Authorized users can update contracts"
ON contracts FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE contracts.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM requests 
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE contracts.request_id = requests.id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- =====================================================
-- RLS POLICIES: negotiation_events
-- =====================================================

-- Users can view negotiation events for their organization's sessions
CREATE POLICY "Users can view negotiation events in their organization"
ON negotiation_events FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM negotiation_sessions 
        JOIN requests ON negotiation_sessions.request_id = requests.id
        JOIN user_accounts ON requests.user_id = user_accounts.id
        WHERE negotiation_sessions.session_id = negotiation_events.session_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can insert negotiation events
CREATE POLICY "System can insert negotiation events"
ON negotiation_events FOR INSERT
WITH CHECK (true);

-- =====================================================
-- RLS POLICIES: audit_logs
-- =====================================================

-- Users can view audit logs for their organization
CREATE POLICY "Users can view audit logs in their organization"
ON audit_logs FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM user_accounts 
        WHERE user_accounts.id = audit_logs.user_id 
        AND user_accounts.organization_id = get_user_organization_id()
    )
    OR is_superuser()
);

-- System can insert audit logs
CREATE POLICY "System can insert audit logs"
ON audit_logs FOR INSERT
WITH CHECK (true);

-- No updates or deletes on audit logs (enforced by triggers)

-- =====================================================
-- RLS POLICIES: policy_configs
-- =====================================================

-- Users can view policies for their organization
CREATE POLICY "Users can view policies in their organization"
ON policy_configs FOR SELECT
USING (
    organization_id = get_user_organization_id()
    OR organization_id IS NULL
    OR is_superuser()
);

-- Admins can create policies for their organization
CREATE POLICY "Admins can create policies for their organization"
ON policy_configs FOR INSERT
WITH CHECK (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- Admins can update policies for their organization
CREATE POLICY "Admins can update policies for their organization"
ON policy_configs FOR UPDATE
USING (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
)
WITH CHECK (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- Admins can delete policies for their organization
CREATE POLICY "Admins can delete policies for their organization"
ON policy_configs FOR DELETE
USING (
    (organization_id = get_user_organization_id() AND has_role('admin'))
    OR is_superuser()
);

-- =====================================================
-- End of RLS policies
-- =====================================================

-- Grant usage on schema to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Grant execute on functions to authenticated users
GRANT EXECUTE ON FUNCTION get_current_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_organization_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_superuser() TO authenticated;
GRANT EXECUTE ON FUNCTION has_role(VARCHAR) TO authenticated;
