-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 01_create_tables.sql
-- Description: Create all database tables
-- =====================================================

-- Enable UUID extension (useful for generating unique IDs)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- TABLE 1: organizations
-- Multi-tenant organization management
-- =====================================================

CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(100),
    size VARCHAR(50),
    country VARCHAR(100),
    billing_email VARCHAR(255),
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT true,
    settings JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE organizations IS 'Multi-tenant organizations for platform isolation';
COMMENT ON COLUMN organizations.organization_id IS 'Unique organization identifier (e.g., acme-corp)';
COMMENT ON COLUMN organizations.plan IS 'Subscription plan: free, pro, enterprise';

-- =====================================================
-- TABLE 2: user_accounts
-- User authentication and authorization
-- =====================================================

CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    
    -- Role and permissions
    role VARCHAR(50) NOT NULL DEFAULT 'buyer',
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    
    -- Organization and team
    organization_id VARCHAR(100),
    team VARCHAR(100),
    
    -- Password policy
    password_changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    password_expires_at TIMESTAMP,
    must_change_password BOOLEAN NOT NULL DEFAULT false,
    
    -- Account security
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    email_verification_token VARCHAR(100),
    
    -- MFA
    mfa_enabled BOOLEAN NOT NULL DEFAULT false,
    mfa_secret VARCHAR(100),
    mfa_backup_codes JSONB,
    
    -- Metadata
    last_login_at TIMESTAMP,
    last_password_change_at TIMESTAMP,
    preferences JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

COMMENT ON TABLE user_accounts IS 'User accounts with authentication and authorization';
COMMENT ON COLUMN user_accounts.role IS 'User role: buyer, approver, admin, vendor';
COMMENT ON COLUMN user_accounts.deleted_at IS 'Soft delete timestamp';

-- =====================================================
-- TABLE 3: user_sessions
-- Session tracking for authenticated users
-- =====================================================

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    
    -- Session data
    refresh_token VARCHAR(200),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    device_type VARCHAR(50),
    location VARCHAR(200),
    
    -- Session state
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE user_sessions IS 'Active user sessions with refresh tokens';

-- =====================================================
-- TABLE 4: api_keys
-- API keys for programmatic access
-- =====================================================

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    
    -- Key details
    name VARCHAR(200) NOT NULL,
    hashed_secret VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    
    -- Permissions and scopes
    scopes JSONB,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Usage tracking
    usage_count INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE api_keys IS 'API keys for programmatic access to the platform';
COMMENT ON COLUMN api_keys.scopes IS 'JSON array of permission scopes';

-- =====================================================
-- TABLE 5: password_history
-- Password history for reuse prevention
-- =====================================================

CREATE TABLE password_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    hashed_password VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE password_history IS 'Password history to prevent password reuse';

-- =====================================================
-- TABLE 6: login_attempts
-- Login attempt tracking for security
-- =====================================================

CREATE TABLE login_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    username VARCHAR(100) NOT NULL,
    
    -- Attempt details
    success BOOLEAN NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    failure_reason VARCHAR(200),
    
    -- MFA
    mfa_required BOOLEAN NOT NULL DEFAULT false,
    mfa_success BOOLEAN,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE login_attempts IS 'Login attempts for security monitoring and brute force detection';

-- =====================================================
-- TABLE 7: oauth_connections
-- OAuth/SSO connections for users
-- =====================================================

CREATE TABLE oauth_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    
    -- Provider details
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    
    -- Tokens
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    
    -- Provider data
    provider_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE oauth_connections IS 'OAuth and SSO connections for federated authentication';

-- =====================================================
-- TABLE 8: requests
-- Procurement requests from buyers
-- =====================================================

CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE RESTRICT,
    
    -- Structured intake fields
    procurement_goal TEXT,
    timeline_deadline TIMESTAMP,
    timeline_urgency VARCHAR(50),
    risk_notes TEXT,
    
    -- Request details
    description TEXT NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    
    -- Budget and quantity
    budget_min NUMERIC(15, 2),
    budget_max NUMERIC(15, 2),
    quantity INTEGER,
    billing_cadence VARCHAR(50),
    
    -- Requirements
    must_haves JSONB,
    nice_to_haves JSONB,
    compliance_requirements JSONB,
    
    -- Additional specifications
    specs JSONB,
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

COMMENT ON TABLE requests IS 'Procurement requests with structured intake data';
COMMENT ON COLUMN requests.timeline_urgency IS 'Urgency level: low, medium, high, critical';
COMMENT ON COLUMN requests.status IS 'Request status: pending, approved, rejected, in_progress, completed';

-- =====================================================
-- TABLE 9: vendor_profiles
-- Vendor information and capabilities
-- =====================================================

CREATE TABLE vendor_profiles (
    id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(100) NOT NULL UNIQUE,
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    description TEXT,
    category VARCHAR(100),
    
    -- Pricing
    list_price NUMERIC(15, 2),
    price_tiers JSONB,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    
    -- Capabilities
    features JSONB,
    integrations JSONB,
    
    -- Compliance
    certifications JSONB,
    compliance_frameworks JSONB,
    
    -- Guardrails and policies
    guardrails JSONB,
    exchange_policy JSONB,
    
    -- Ratings and metadata
    rating NUMERIC(3, 2),
    review_count INTEGER,
    vendor_metadata JSONB,
    
    -- Data quality
    confidence_score NUMERIC(3, 2),
    data_source VARCHAR(100),
    last_enriched_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

COMMENT ON TABLE vendor_profiles IS 'Vendor catalog with capabilities and compliance data';
COMMENT ON COLUMN vendor_profiles.guardrails IS 'Pricing guardrails and negotiation boundaries';
COMMENT ON COLUMN vendor_profiles.exchange_policy IS 'Vendor negotiation policies and preferences';

-- =====================================================
-- TABLE 10: negotiation_sessions
-- Negotiation session tracking
-- =====================================================

CREATE TABLE negotiation_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    vendor_id INTEGER NOT NULL REFERENCES vendor_profiles(id) ON DELETE CASCADE,
    
    -- Session state
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    current_round INTEGER NOT NULL DEFAULT 1,
    max_rounds INTEGER NOT NULL DEFAULT 8,
    
    -- Outcome
    outcome VARCHAR(50),
    outcome_reason TEXT,
    final_offer_id INTEGER,
    
    -- Negotiation state
    buyer_state JSONB,
    seller_state JSONB,
    opponent_model JSONB,
    
    -- Timing
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Summary metrics
    total_messages INTEGER NOT NULL DEFAULT 0,
    savings_achieved NUMERIC(15, 2),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT uq_negotiation_request_vendor UNIQUE (request_id, vendor_id)
);

COMMENT ON TABLE negotiation_sessions IS 'Negotiation sessions between buyers and vendors';
COMMENT ON COLUMN negotiation_sessions.status IS 'Session status: active, completed, failed, cancelled';
COMMENT ON COLUMN negotiation_sessions.outcome IS 'Final outcome: accepted, rejected, timeout, cancelled';

-- =====================================================
-- TABLE 11: offers
-- Negotiation offers between buyers and vendors
-- =====================================================

CREATE TABLE offers (
    id SERIAL PRIMARY KEY,
    offer_id VARCHAR(100) NOT NULL UNIQUE,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    vendor_id INTEGER NOT NULL REFERENCES vendor_profiles(id) ON DELETE CASCADE,
    negotiation_session_id INTEGER REFERENCES negotiation_sessions(id) ON DELETE CASCADE,
    
    -- Offer components
    unit_price NUMERIC(15, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    term_months INTEGER NOT NULL,
    payment_terms VARCHAR(50) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    
    -- Additional terms
    discount_percent NUMERIC(5, 2),
    value_adds JSONB,
    conditions JSONB,
    
    -- Scoring and evaluation
    score NUMERIC(5, 2),
    utility_buyer NUMERIC(5, 2),
    utility_seller NUMERIC(5, 2),
    tco NUMERIC(15, 2),
    
    -- Status
    accepted BOOLEAN NOT NULL DEFAULT false,
    rejected BOOLEAN NOT NULL DEFAULT false,
    round_number INTEGER,
    actor VARCHAR(50),
    
    -- Rationale
    rationale JSONB,
    strategy VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

COMMENT ON TABLE offers IS 'Negotiation offers with pricing and terms';
COMMENT ON COLUMN offers.actor IS 'Who made the offer: buyer or seller';
COMMENT ON COLUMN offers.payment_terms IS 'Payment terms: NET30, NET15, NET60, upfront, etc.';
COMMENT ON COLUMN offers.tco IS 'Total cost of ownership';

-- Add foreign key for final_offer_id (must be added after offers table exists)
ALTER TABLE negotiation_sessions 
ADD CONSTRAINT fk_negotiation_sessions_final_offer 
FOREIGN KEY (final_offer_id) REFERENCES offers(id) ON DELETE SET NULL;

-- =====================================================
-- TABLE 12: contracts
-- Finalized contracts and agreements
-- =====================================================

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(100) NOT NULL UNIQUE,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE RESTRICT,
    vendor_id INTEGER NOT NULL REFERENCES vendor_profiles(id) ON DELETE RESTRICT,
    final_offer_id INTEGER REFERENCES offers(id) ON DELETE SET NULL,
    
    -- Contract terms (denormalized from final offer)
    unit_price NUMERIC(15, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    term_months INTEGER NOT NULL,
    payment_terms VARCHAR(50) NOT NULL,
    total_value NUMERIC(15, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    
    -- Contract details
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    renewal_date TIMESTAMP,
    auto_renew BOOLEAN NOT NULL DEFAULT false,
    
    -- Document management
    document_url VARCHAR(500),
    document_hash VARCHAR(64),
    template_version VARCHAR(50),
    
    -- Signature tracking
    signed_by_buyer BOOLEAN NOT NULL DEFAULT false,
    signed_by_vendor BOOLEAN NOT NULL DEFAULT false,
    buyer_signature_date TIMESTAMP,
    vendor_signature_date TIMESTAMP,
    docusign_envelope_id VARCHAR(100),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    
    -- ERP integration
    purchase_order_id VARCHAR(100),
    erp_sync_status VARCHAR(50),
    erp_synced_at TIMESTAMP,
    
    -- Additional terms
    value_adds JSONB,
    special_terms JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

COMMENT ON TABLE contracts IS 'Finalized contracts with signature and ERP integration';
COMMENT ON COLUMN contracts.status IS 'Contract status: draft, pending_signature, active, expired, terminated';
COMMENT ON COLUMN contracts.document_hash IS 'SHA-256 hash of contract document for integrity verification';

-- =====================================================
-- TABLE 13: negotiation_events
-- Real-time negotiation events for streaming
-- =====================================================

CREATE TABLE negotiation_events (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE negotiation_events IS 'Real-time events for negotiation streaming and audit';
COMMENT ON COLUMN negotiation_events.event_type IS 'Event type: offer_made, offer_accepted, round_complete, etc.';

-- =====================================================
-- TABLE 14: audit_logs
-- Comprehensive audit trail for all actions
-- =====================================================

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    
    -- Actor information
    user_id INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    actor_type VARCHAR(50) NOT NULL,
    actor_id VARCHAR(100),
    
    -- Action details
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    
    -- Context
    negotiation_session_id INTEGER REFERENCES negotiation_sessions(id) ON DELETE SET NULL,
    
    -- Event data
    event_data JSONB,
    changes JSONB,
    
    -- Metadata
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Immutable audit log for compliance and security';
COMMENT ON COLUMN audit_logs.actor_type IS 'Actor type: user, system, agent';
COMMENT ON COLUMN audit_logs.changes IS 'JSON object showing before/after values';

-- =====================================================
-- TABLE 15: policy_configs
-- Policy configuration storage
-- =====================================================

CREATE TABLE policy_configs (
    id SERIAL PRIMARY KEY,
    
    -- Policy identification
    policy_name VARCHAR(100) NOT NULL,
    policy_type VARCHAR(50) NOT NULL,
    organization_id VARCHAR(100),
    
    -- Policy content
    policy_data JSONB NOT NULL,
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Metadata
    description TEXT,
    created_by INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT uq_policy_org_version UNIQUE (policy_name, organization_id, version)
);

COMMENT ON TABLE policy_configs IS 'Versioned policy configurations for governance';
COMMENT ON COLUMN policy_configs.policy_type IS 'Policy type: budget, approval, compliance, negotiation';

-- =====================================================
-- End of table creation
-- =====================================================
