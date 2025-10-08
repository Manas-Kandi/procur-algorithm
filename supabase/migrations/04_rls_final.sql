-- =====================================================
-- FINAL RLS IMPLEMENTATION - EXPLICIT CASTING
-- =====================================================

-- Drop everything
DO $$ 
DECLARE r RECORD;
BEGIN
    FOR r IN (SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I', r.policyname, r.schemaname, r.tablename);
    END LOOP;
END $$;

DROP FUNCTION IF EXISTS get_current_user_id() CASCADE;
DROP FUNCTION IF EXISTS get_user_organization_id() CASCADE;
DROP FUNCTION IF EXISTS is_superuser() CASCADE;
DROP FUNCTION IF EXISTS has_role(TEXT) CASCADE;
DROP FUNCTION IF EXISTS has_role(VARCHAR) CASCADE;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

CREATE FUNCTION get_current_user_id()
RETURNS INTEGER
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT id FROM user_accounts 
    WHERE email = COALESCE(auth.jwt()->>'email', '')
    AND deleted_at IS NULL
    LIMIT 1;
$$;

CREATE FUNCTION get_user_organization_id()
RETURNS VARCHAR(100)
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT organization_id FROM user_accounts 
    WHERE id = get_current_user_id()
    AND deleted_at IS NULL;
$$;

CREATE FUNCTION is_superuser()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT COALESCE(
        (SELECT is_superuser FROM user_accounts WHERE id = get_current_user_id() AND deleted_at IS NULL),
        false
    );
$$;

CREATE FUNCTION has_role(required_role VARCHAR)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT COALESCE(
        (SELECT (role = required_role OR is_superuser = true) FROM user_accounts WHERE id = get_current_user_id() AND deleted_at IS NULL),
        false
    );
$$;

-- =====================================================
-- ENABLE RLS
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
-- POLICIES
-- =====================================================

-- Organizations
CREATE POLICY org_select ON organizations FOR SELECT USING (organization_id = get_user_organization_id() OR is_superuser());
CREATE POLICY org_insert ON organizations FOR INSERT WITH CHECK (is_superuser());
CREATE POLICY org_update ON organizations FOR UPDATE USING (organization_id = get_user_organization_id() AND has_role('admin')) WITH CHECK (organization_id = get_user_organization_id() AND has_role('admin'));
CREATE POLICY org_delete ON organizations FOR DELETE USING (is_superuser());

-- User Accounts
CREATE POLICY user_select ON user_accounts FOR SELECT USING (organization_id = get_user_organization_id() OR is_superuser() OR id = get_current_user_id());
CREATE POLICY user_insert ON user_accounts FOR INSERT WITH CHECK ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());
CREATE POLICY user_update ON user_accounts FOR UPDATE USING (id = get_current_user_id() OR (organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser()) WITH CHECK (id = get_current_user_id() OR (organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());
CREATE POLICY user_delete ON user_accounts FOR DELETE USING ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());

-- User Sessions
CREATE POLICY session_select ON user_sessions FOR SELECT USING (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY session_insert ON user_sessions FOR INSERT WITH CHECK (user_id = get_current_user_id());
CREATE POLICY session_update ON user_sessions FOR UPDATE USING (user_id = get_current_user_id() OR is_superuser()) WITH CHECK (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY session_delete ON user_sessions FOR DELETE USING (user_id = get_current_user_id() OR is_superuser());

-- API Keys
CREATE POLICY apikey_select ON api_keys FOR SELECT USING (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY apikey_insert ON api_keys FOR INSERT WITH CHECK (user_id = get_current_user_id());
CREATE POLICY apikey_update ON api_keys FOR UPDATE USING (user_id = get_current_user_id() OR is_superuser()) WITH CHECK (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY apikey_delete ON api_keys FOR DELETE USING (user_id = get_current_user_id() OR is_superuser());

-- Password History
CREATE POLICY pwdhist_select ON password_history FOR SELECT USING (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY pwdhist_insert ON password_history FOR INSERT WITH CHECK (user_id = get_current_user_id() OR is_superuser());

-- Login Attempts
CREATE POLICY login_select ON login_attempts FOR SELECT USING (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY login_insert ON login_attempts FOR INSERT WITH CHECK (true);

-- OAuth Connections
CREATE POLICY oauth_select ON oauth_connections FOR SELECT USING (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY oauth_insert ON oauth_connections FOR INSERT WITH CHECK (user_id = get_current_user_id());
CREATE POLICY oauth_update ON oauth_connections FOR UPDATE USING (user_id = get_current_user_id() OR is_superuser()) WITH CHECK (user_id = get_current_user_id() OR is_superuser());
CREATE POLICY oauth_delete ON oauth_connections FOR DELETE USING (user_id = get_current_user_id() OR is_superuser());

-- Requests
CREATE POLICY req_select ON requests FOR SELECT USING (EXISTS (SELECT 1 FROM user_accounts WHERE user_accounts.id = requests.user_id AND user_accounts.organization_id = get_user_organization_id() AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY req_insert ON requests FOR INSERT WITH CHECK (user_id = get_current_user_id());
CREATE POLICY req_update ON requests FOR UPDATE USING (user_id = get_current_user_id() OR has_role('approver') OR has_role('admin') OR is_superuser()) WITH CHECK (user_id = get_current_user_id() OR has_role('approver') OR has_role('admin') OR is_superuser());
CREATE POLICY req_delete ON requests FOR DELETE USING (user_id = get_current_user_id() OR has_role('admin') OR is_superuser());

-- Vendor Profiles
CREATE POLICY vendor_select ON vendor_profiles FOR SELECT USING (get_current_user_id() IS NOT NULL);
CREATE POLICY vendor_insert ON vendor_profiles FOR INSERT WITH CHECK (has_role('admin') OR is_superuser());
CREATE POLICY vendor_update ON vendor_profiles FOR UPDATE USING (has_role('admin') OR is_superuser()) WITH CHECK (has_role('admin') OR is_superuser());
CREATE POLICY vendor_delete ON vendor_profiles FOR DELETE USING (is_superuser());

-- Negotiation Sessions
CREATE POLICY negsess_select ON negotiation_sessions FOR SELECT USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE negotiation_sessions.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY negsess_insert ON negotiation_sessions FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE requests.id = request_id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY negsess_update ON negotiation_sessions FOR UPDATE USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE negotiation_sessions.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser()) WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE negotiation_sessions.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());

-- Offers
CREATE POLICY offer_select ON offers FOR SELECT USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE offers.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY offer_insert ON offers FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE requests.id = request_id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY offer_update ON offers FOR UPDATE USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE offers.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser()) WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE offers.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());

-- Contracts
CREATE POLICY contract_select ON contracts FOR SELECT USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE contracts.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY contract_insert ON contracts FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE requests.id = request_id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY contract_update ON contracts FOR UPDATE USING (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE contracts.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser()) WITH CHECK (EXISTS (SELECT 1 FROM requests JOIN user_accounts ON requests.user_id = user_accounts.id WHERE contracts.request_id = requests.id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());

-- Negotiation Events
CREATE POLICY negevent_select ON negotiation_events FOR SELECT USING (EXISTS (SELECT 1 FROM negotiation_sessions JOIN requests ON negotiation_sessions.request_id = requests.id JOIN user_accounts ON requests.user_id = user_accounts.id WHERE negotiation_sessions.session_id = negotiation_events.session_id AND user_accounts.organization_id = get_user_organization_id() AND requests.deleted_at IS NULL AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY negevent_insert ON negotiation_events FOR INSERT WITH CHECK (true);

-- Audit Logs
CREATE POLICY audit_select ON audit_logs FOR SELECT USING (EXISTS (SELECT 1 FROM user_accounts WHERE user_accounts.id = audit_logs.user_id AND user_accounts.organization_id = get_user_organization_id() AND user_accounts.deleted_at IS NULL) OR is_superuser());
CREATE POLICY audit_insert ON audit_logs FOR INSERT WITH CHECK (true);

-- Policy Configs
CREATE POLICY policy_select ON policy_configs FOR SELECT USING (organization_id = get_user_organization_id() OR organization_id IS NULL OR is_superuser());
CREATE POLICY policy_insert ON policy_configs FOR INSERT WITH CHECK ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());
CREATE POLICY policy_update ON policy_configs FOR UPDATE USING ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser()) WITH CHECK ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());
CREATE POLICY policy_delete ON policy_configs FOR DELETE USING ((organization_id = get_user_organization_id() AND has_role('admin')) OR is_superuser());

-- =====================================================
-- GRANTS
-- =====================================================

GRANT USAGE ON SCHEMA public TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_current_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_organization_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_superuser() TO authenticated;
GRANT EXECUTE ON FUNCTION has_role(VARCHAR) TO authenticated;

SELECT 'RLS setup complete' AS status;
