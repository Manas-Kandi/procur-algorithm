-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 06_seed_fixed.sql
-- Description: Sample seed data - FIXED VERSION
-- =====================================================

-- Clear existing data first
DELETE FROM negotiation_events;
DELETE FROM audit_logs;
DELETE FROM policy_configs;
DELETE FROM offers;
DELETE FROM contracts;
DELETE FROM negotiation_sessions;
DELETE FROM requests;
DELETE FROM vendor_profiles;
DELETE FROM oauth_connections;
DELETE FROM login_attempts;
DELETE FROM password_history;
DELETE FROM api_keys;
DELETE FROM user_sessions;
DELETE FROM user_accounts;
DELETE FROM organizations;

-- Reset sequences
ALTER SEQUENCE organizations_id_seq RESTART WITH 1;
ALTER SEQUENCE user_accounts_id_seq RESTART WITH 1;
ALTER SEQUENCE requests_id_seq RESTART WITH 1;
ALTER SEQUENCE vendor_profiles_id_seq RESTART WITH 1;
ALTER SEQUENCE negotiation_sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE offers_id_seq RESTART WITH 1;
ALTER SEQUENCE contracts_id_seq RESTART WITH 1;
ALTER SEQUENCE negotiation_events_id_seq RESTART WITH 1;
ALTER SEQUENCE audit_logs_id_seq RESTART WITH 1;
ALTER SEQUENCE policy_configs_id_seq RESTART WITH 1;

-- =====================================================
-- SAMPLE ORGANIZATIONS
-- =====================================================

INSERT INTO organizations (organization_id, name, plan, is_active, settings)
VALUES 
    ('demo-org', 'Demo Organization', 'pro', true, '{"features": ["ai_negotiation", "analytics", "integrations"]}'),
    ('acme-corp', 'Acme Corporation', 'enterprise', true, '{"features": ["ai_negotiation", "analytics", "integrations", "custom_policies"]}');

-- =====================================================
-- SAMPLE USERS
-- =====================================================

INSERT INTO user_accounts (email, username, hashed_password, full_name, role, organization_id, is_active, email_verified, is_superuser)
VALUES 
    ('admin@demo-org.com', 'demo_admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', 'Demo Admin', 'admin', 'demo-org', true, true, false),
    ('buyer@demo-org.com', 'demo_buyer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', 'Demo Buyer', 'buyer', 'demo-org', true, true, false),
    ('approver@demo-org.com', 'demo_approver', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', 'Demo Approver', 'approver', 'demo-org', true, true, false),
    ('admin@acme-corp.com', 'acme_admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', 'Acme Admin', 'admin', 'acme-corp', true, true, false),
    ('superuser@procur.com', 'superuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', 'Super User', 'admin', 'demo-org', true, true, true);

-- =====================================================
-- SAMPLE VENDOR PROFILES
-- =====================================================

INSERT INTO vendor_profiles (vendor_id, name, website, description, category, list_price, currency, features, certifications, rating, review_count, confidence_score)
VALUES 
    ('salesforce', 'Salesforce', 'https://www.salesforce.com', 'Leading CRM platform', 'crm', 150.00, 'USD', '["api", "mobile", "analytics"]'::jsonb, '["SOC2", "ISO27001"]'::jsonb, 4.5, 1250, 0.95),
    ('hubspot', 'HubSpot', 'https://www.hubspot.com', 'All-in-one CRM platform', 'crm', 120.00, 'USD', '["api", "mobile", "marketing"]'::jsonb, '["SOC2", "ISO27001"]'::jsonb, 4.3, 980, 0.92),
    ('slack', 'Slack', 'https://slack.com', 'Team collaboration platform', 'collaboration', 8.00, 'USD', '["api", "mobile", "integrations"]'::jsonb, '["SOC2", "ISO27001"]'::jsonb, 4.6, 2100, 0.98),
    ('zoom', 'Zoom', 'https://zoom.us', 'Video conferencing platform', 'collaboration', 15.00, 'USD', '["video", "webinar", "recording"]'::jsonb, '["SOC2", "ISO27001"]'::jsonb, 4.4, 1800, 0.96),
    ('aws', 'Amazon Web Services', 'https://aws.amazon.com', 'Cloud computing services', 'cloud', 0.10, 'USD', '["compute", "storage", "database"]'::jsonb, '["SOC2", "ISO27001", "FedRAMP"]'::jsonb, 4.7, 3500, 0.99);

-- =====================================================
-- SAMPLE REQUESTS
-- =====================================================

INSERT INTO requests (request_id, user_id, description, request_type, category, budget_min, budget_max, quantity, billing_cadence, must_haves, nice_to_haves, compliance_requirements, status, procurement_goal, timeline_urgency)
SELECT 
    'req-001',
    (SELECT id FROM user_accounts WHERE email = 'buyer@demo-org.com'),
    'Need a CRM system for our sales team of 50 people',
    'saas', 'crm', 5000.00, 8000.00, 50, 'monthly',
    '["api_integration", "mobile_app", "reporting"]'::jsonb,
    '["ai_features", "custom_workflows"]'::jsonb,
    '["SOC2", "GDPR"]'::jsonb,
    'pending',
    'Improve sales team productivity',
    'high';

INSERT INTO requests (request_id, user_id, description, request_type, category, budget_min, budget_max, quantity, billing_cadence, must_haves, nice_to_haves, compliance_requirements, status, procurement_goal, timeline_urgency)
SELECT 
    'req-002',
    (SELECT id FROM user_accounts WHERE email = 'buyer@demo-org.com'),
    'Video conferencing solution for remote team',
    'saas', 'collaboration', 500.00, 1500.00, 100, 'monthly',
    '["screen_sharing", "recording", "mobile_support"]'::jsonb,
    '["webinar_features", "breakout_rooms"]'::jsonb,
    '["SOC2"]'::jsonb,
    'approved',
    'Enable effective remote collaboration',
    'medium';

INSERT INTO requests (request_id, user_id, description, request_type, category, budget_min, budget_max, quantity, billing_cadence, must_haves, nice_to_haves, compliance_requirements, status, procurement_goal, timeline_urgency)
SELECT 
    'req-003',
    (SELECT id FROM user_accounts WHERE email = 'admin@acme-corp.com'),
    'Cloud infrastructure for new application',
    'infrastructure', 'cloud', 2000.00, 5000.00, 1, 'monthly',
    '["auto_scaling", "load_balancing", "monitoring"]'::jsonb,
    '["managed_database", "cdn"]'::jsonb,
    '["SOC2", "ISO27001"]'::jsonb,
    'pending',
    'Deploy scalable infrastructure',
    'critical';

-- =====================================================
-- SAMPLE NEGOTIATION SESSIONS
-- =====================================================

INSERT INTO negotiation_sessions (session_id, request_id, vendor_id, status, current_round, max_rounds, buyer_state, seller_state, started_at)
SELECT 
    'session-001',
    (SELECT id FROM requests WHERE request_id = 'req-001'),
    (SELECT id FROM vendor_profiles WHERE vendor_id = 'salesforce'),
    'active', 2, 8,
    '{"target_price": 140, "max_price": 150}'::jsonb,
    '{"min_price": 135, "target_price": 145}'::jsonb,
    NOW() - INTERVAL '2 hours';

INSERT INTO negotiation_sessions (session_id, request_id, vendor_id, status, current_round, max_rounds, buyer_state, seller_state, started_at, completed_at, outcome)
SELECT 
    'session-002',
    (SELECT id FROM requests WHERE request_id = 'req-001'),
    (SELECT id FROM vendor_profiles WHERE vendor_id = 'hubspot'),
    'completed', 5, 8,
    '{"target_price": 110, "max_price": 120}'::jsonb,
    '{"min_price": 105, "target_price": 115}'::jsonb,
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '23 hours',
    'accepted';

INSERT INTO negotiation_sessions (session_id, request_id, vendor_id, status, current_round, max_rounds, buyer_state, seller_state, started_at)
SELECT 
    'session-003',
    (SELECT id FROM requests WHERE request_id = 'req-002'),
    (SELECT id FROM vendor_profiles WHERE vendor_id = 'zoom'),
    'active', 1, 8,
    '{"target_price": 12, "max_price": 15}'::jsonb,
    '{"min_price": 13, "target_price": 14}'::jsonb,
    NOW() - INTERVAL '30 minutes';

-- =====================================================
-- SAMPLE OFFERS
-- =====================================================

INSERT INTO offers (offer_id, request_id, vendor_id, negotiation_session_id, unit_price, quantity, term_months, payment_terms, currency, discount_percent, value_adds, score, utility_buyer, utility_seller, accepted, rejected, round_number, actor, strategy)
SELECT 
    'offer-001',
    (SELECT id FROM requests WHERE request_id = 'req-001'),
    (SELECT id FROM vendor_profiles WHERE vendor_id = 'salesforce'),
    (SELECT id FROM negotiation_sessions WHERE session_id = 'session-001'),
    150.00, 50, 12, 'NET30', 'USD', 0,
    '["onboarding", "training"]'::jsonb,
    85.5, 0.75, 0.95, false, false, 1, 'seller', 'value_based';

INSERT INTO offers (offer_id, request_id, vendor_id, negotiation_session_id, unit_price, quantity, term_months, payment_terms, currency, discount_percent, value_adds, score, utility_buyer, utility_seller, accepted, rejected, round_number, actor, strategy)
SELECT 
    'offer-002',
    (SELECT id FROM requests WHERE request_id = 'req-001'),
    (SELECT id FROM vendor_profiles WHERE vendor_id = 'salesforce'),
    (SELECT id FROM negotiation_sessions WHERE session_id = 'session-001'),
    142.00, 50, 12, 'NET30', 'USD', 5.3,
    '["onboarding", "training", "priority_support"]'::jsonb,
    88.2, 0.82, 0.88, false, false, 2, 'seller', 'collaborative';

-- =====================================================
-- SAMPLE NEGOTIATION EVENTS
-- =====================================================

INSERT INTO negotiation_events (session_id, event_type, event_data)
VALUES 
    ('session-001', 'session_started', '{"actor": "system", "details": "Negotiation initiated"}'::jsonb),
    ('session-001', 'offer_made', '{"actor": "seller", "offer_id": "offer-001", "round": 1, "price": 150.00}'::jsonb),
    ('session-002', 'session_started', '{"actor": "system", "details": "Negotiation initiated"}'::jsonb),
    ('session-002', 'session_completed', '{"actor": "system", "outcome": "accepted"}'::jsonb);

-- =====================================================
-- SAMPLE POLICY CONFIGS
-- =====================================================

INSERT INTO policy_configs (policy_name, policy_type, organization_id, policy_data, version, is_active, description, created_by)
SELECT 
    'budget_approval_policy',
    'approval',
    'demo-org',
    '{"rules": [{"threshold": 5000, "approvers": 1}]}'::jsonb,
    1, true,
    'Budget approval thresholds',
    (SELECT id FROM user_accounts WHERE email = 'admin@demo-org.com');

-- =====================================================
-- SAMPLE AUDIT LOGS
-- =====================================================

INSERT INTO audit_logs (user_id, actor_type, action, resource_type, resource_id, event_data, ip_address)
SELECT 
    (SELECT id FROM user_accounts WHERE email = 'buyer@demo-org.com'),
    'user', 'create_request', 'request', 'req-001',
    '{"category": "crm", "budget_max": 8000}'::jsonb,
    '192.168.1.100';

SELECT 'Sample data seeded successfully!' AS status,
       (SELECT COUNT(*) FROM organizations) AS organizations,
       (SELECT COUNT(*) FROM user_accounts) AS users,
       (SELECT COUNT(*) FROM vendor_profiles) AS vendors,
       (SELECT COUNT(*) FROM requests) AS requests,
       (SELECT COUNT(*) FROM negotiation_sessions) AS sessions,
       (SELECT COUNT(*) FROM offers) AS offers;
