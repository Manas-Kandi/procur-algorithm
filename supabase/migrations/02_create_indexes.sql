-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 02_create_indexes.sql
-- Description: Create indexes for performance optimization
-- =====================================================

-- =====================================================
-- INDEXES FOR: organizations
-- =====================================================

CREATE INDEX idx_organizations_organization_id ON organizations(organization_id);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);
CREATE INDEX idx_organizations_plan ON organizations(plan);

-- =====================================================
-- INDEXES FOR: user_accounts
-- =====================================================

CREATE INDEX idx_user_accounts_email ON user_accounts(email);
CREATE INDEX idx_user_accounts_username ON user_accounts(username);
CREATE INDEX idx_user_accounts_organization_id ON user_accounts(organization_id);
CREATE INDEX idx_user_accounts_role ON user_accounts(role);
CREATE INDEX idx_user_accounts_is_active ON user_accounts(is_active);
CREATE INDEX idx_user_accounts_deleted_at ON user_accounts(deleted_at) WHERE deleted_at IS NULL;

-- =====================================================
-- INDEXES FOR: user_sessions
-- =====================================================

CREATE INDEX idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- =====================================================
-- INDEXES FOR: api_keys
-- =====================================================

CREATE INDEX idx_api_keys_key_id ON api_keys(key_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

-- =====================================================
-- INDEXES FOR: password_history
-- =====================================================

CREATE INDEX idx_password_history_user_id ON password_history(user_id);
CREATE INDEX idx_password_history_changed_at ON password_history(changed_at DESC);

-- =====================================================
-- INDEXES FOR: login_attempts
-- =====================================================

CREATE INDEX idx_login_attempts_username ON login_attempts(username);
CREATE INDEX idx_login_attempts_user_id ON login_attempts(user_id);
CREATE INDEX idx_login_attempts_created_at ON login_attempts(created_at DESC);
CREATE INDEX idx_login_attempts_success ON login_attempts(success);
CREATE INDEX idx_login_attempts_ip_address ON login_attempts(ip_address);

-- =====================================================
-- INDEXES FOR: oauth_connections
-- =====================================================

CREATE INDEX idx_oauth_connections_user_id ON oauth_connections(user_id);
CREATE INDEX idx_oauth_connections_provider ON oauth_connections(provider);
CREATE INDEX idx_oauth_connections_provider_user_id ON oauth_connections(provider, provider_user_id);

-- =====================================================
-- INDEXES FOR: requests
-- =====================================================

CREATE INDEX idx_requests_request_id ON requests(request_id);
CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_requests_category ON requests(category);
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX idx_requests_deleted_at ON requests(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_requests_timeline_deadline ON requests(timeline_deadline);
CREATE INDEX idx_requests_timeline_urgency ON requests(timeline_urgency);

-- GIN index for JSONB columns
CREATE INDEX idx_requests_must_haves_gin ON requests USING GIN (must_haves);
CREATE INDEX idx_requests_compliance_requirements_gin ON requests USING GIN (compliance_requirements);

-- =====================================================
-- INDEXES FOR: vendor_profiles
-- =====================================================

CREATE INDEX idx_vendor_profiles_vendor_id ON vendor_profiles(vendor_id);
CREATE INDEX idx_vendor_profiles_name ON vendor_profiles(name);
CREATE INDEX idx_vendor_profiles_category ON vendor_profiles(category);
CREATE INDEX idx_vendor_profiles_deleted_at ON vendor_profiles(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_vendor_profiles_rating ON vendor_profiles(rating DESC);

-- GIN indexes for JSONB columns
CREATE INDEX idx_vendor_profiles_features_gin ON vendor_profiles USING GIN (features);
CREATE INDEX idx_vendor_profiles_certifications_gin ON vendor_profiles USING GIN (certifications);

-- Text search index for vendor name
CREATE INDEX idx_vendor_profiles_name_trgm ON vendor_profiles USING GIN (name gin_trgm_ops);

-- =====================================================
-- INDEXES FOR: negotiation_sessions
-- =====================================================

CREATE INDEX idx_negotiation_sessions_session_id ON negotiation_sessions(session_id);
CREATE INDEX idx_negotiation_sessions_request_id ON negotiation_sessions(request_id);
CREATE INDEX idx_negotiation_sessions_vendor_id ON negotiation_sessions(vendor_id);
CREATE INDEX idx_negotiation_sessions_status ON negotiation_sessions(status);
CREATE INDEX idx_negotiation_sessions_outcome ON negotiation_sessions(outcome);
CREATE INDEX idx_negotiation_sessions_started_at ON negotiation_sessions(started_at DESC);
CREATE INDEX idx_negotiation_sessions_deleted_at ON negotiation_sessions(deleted_at) WHERE deleted_at IS NULL;

-- =====================================================
-- INDEXES FOR: offers
-- =====================================================

CREATE INDEX idx_offers_offer_id ON offers(offer_id);
CREATE INDEX idx_offers_request_id ON offers(request_id);
CREATE INDEX idx_offers_vendor_id ON offers(vendor_id);
CREATE INDEX idx_offers_negotiation_session_id ON offers(negotiation_session_id);
CREATE INDEX idx_offers_accepted ON offers(accepted);
CREATE INDEX idx_offers_rejected ON offers(rejected);
CREATE INDEX idx_offers_round_number ON offers(round_number);
CREATE INDEX idx_offers_created_at ON offers(created_at DESC);
CREATE INDEX idx_offers_deleted_at ON offers(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_offers_score ON offers(score DESC);

-- Composite index for active offers
CREATE INDEX idx_offers_active ON offers(request_id, vendor_id, accepted, rejected) 
WHERE deleted_at IS NULL;

-- =====================================================
-- INDEXES FOR: contracts
-- =====================================================

CREATE INDEX idx_contracts_contract_id ON contracts(contract_id);
CREATE INDEX idx_contracts_request_id ON contracts(request_id);
CREATE INDEX idx_contracts_vendor_id ON contracts(vendor_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_created_at ON contracts(created_at DESC);
CREATE INDEX idx_contracts_deleted_at ON contracts(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_contracts_end_date ON contracts(end_date);
CREATE INDEX idx_contracts_renewal_date ON contracts(renewal_date);
CREATE INDEX idx_contracts_purchase_order_id ON contracts(purchase_order_id);

-- Index for signature tracking
CREATE INDEX idx_contracts_signatures ON contracts(signed_by_buyer, signed_by_vendor);

-- =====================================================
-- INDEXES FOR: negotiation_events
-- =====================================================

CREATE INDEX idx_negotiation_events_session_id ON negotiation_events(session_id);
CREATE INDEX idx_negotiation_events_event_type ON negotiation_events(event_type);
CREATE INDEX idx_negotiation_events_created_at ON negotiation_events(created_at DESC);

-- GIN index for event_data
CREATE INDEX idx_negotiation_events_event_data_gin ON negotiation_events USING GIN (event_data);

-- =====================================================
-- INDEXES FOR: audit_logs
-- =====================================================

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_actor_type ON audit_logs(actor_type);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_negotiation_session_id ON audit_logs(negotiation_session_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Composite index for resource lookups
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- GIN index for event_data
CREATE INDEX idx_audit_logs_event_data_gin ON audit_logs USING GIN (event_data);

-- =====================================================
-- INDEXES FOR: policy_configs
-- =====================================================

CREATE INDEX idx_policy_configs_policy_name ON policy_configs(policy_name);
CREATE INDEX idx_policy_configs_policy_type ON policy_configs(policy_type);
CREATE INDEX idx_policy_configs_organization_id ON policy_configs(organization_id);
CREATE INDEX idx_policy_configs_is_active ON policy_configs(is_active);
CREATE INDEX idx_policy_configs_deleted_at ON policy_configs(deleted_at) WHERE deleted_at IS NULL;

-- Composite index for active policies
CREATE INDEX idx_policy_configs_active ON policy_configs(organization_id, policy_type, is_active) 
WHERE deleted_at IS NULL;

-- GIN index for policy_data
CREATE INDEX idx_policy_configs_policy_data_gin ON policy_configs USING GIN (policy_data);

-- =====================================================
-- End of index creation
-- =====================================================

-- Analyze tables to update statistics
ANALYZE organizations;
ANALYZE user_accounts;
ANALYZE user_sessions;
ANALYZE api_keys;
ANALYZE password_history;
ANALYZE login_attempts;
ANALYZE oauth_connections;
ANALYZE requests;
ANALYZE vendor_profiles;
ANALYZE negotiation_sessions;
ANALYZE offers;
ANALYZE contracts;
ANALYZE negotiation_events;
ANALYZE audit_logs;
ANALYZE policy_configs;
