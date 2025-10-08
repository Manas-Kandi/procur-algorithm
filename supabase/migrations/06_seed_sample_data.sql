-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 06_seed_sample_data.sql
-- Description: Sample seed data for testing (OPTIONAL)
-- =====================================================

-- NOTE: This file is OPTIONAL and for testing purposes only
-- You can skip this file if you want to start with an empty database

-- =====================================================
-- SAMPLE ORGANIZATION
-- =====================================================

INSERT INTO organizations (organization_id, name, plan, is_active, settings)
VALUES 
    ('demo-org', 'Demo Organization', 'pro', true, '{"features": ["ai_negotiation", "analytics", "integrations"]}')
ON CONFLICT (organization_id) DO NOTHING;

INSERT INTO organizations (organization_id, name, plan, is_active, settings)
VALUES 
    ('acme-corp', 'Acme Corporation', 'enterprise', true, '{"features": ["ai_negotiation", "analytics", "integrations", "custom_policies"]}')
ON CONFLICT (organization_id) DO NOTHING;

-- =====================================================
-- SAMPLE USERS
-- =====================================================

-- NOTE: Password is 'password123' hashed with bcrypt
-- In production, use proper password hashing!
-- You can generate bcrypt hashes at: https://bcrypt-generator.com/

INSERT INTO user_accounts (
    email, username, hashed_password, full_name,
    role, organization_id, is_active, email_verified, is_superuser
)
VALUES 
    -- Demo Org Users
    (
        'admin@demo-org.com', 
        'demo_admin',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia', -- password123
        'Demo Admin',
        'admin',
        'demo-org',
        true,
        true,
        false
    ),
    (
        'buyer@demo-org.com',
        'demo_buyer',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia',
        'Demo Buyer',
        'buyer',
        'demo-org',
        true,
        true,
        false
    ),
    (
        'approver@demo-org.com',
        'demo_approver',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia',
        'Demo Approver',
        'approver',
        'demo-org',
        true,
        true,
        false
    ),
    
    -- Acme Corp Users
    (
        'admin@acme-corp.com',
        'acme_admin',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia',
        'Acme Admin',
        'admin',
        'acme-corp',
        true,
        true,
        false
    ),
    
    -- Superuser
    (
        'superuser@procur.com',
        'superuser',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ3pia',
        'Super User',
        'admin',
        'demo-org',
        true,
        true,
        true
    )
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- SAMPLE VENDOR PROFILES
-- =====================================================

INSERT INTO vendor_profiles (
    vendor_id, name, website, description, category,
    list_price, currency, features, certifications,
    rating, review_count, confidence_score
)
VALUES 
    (
        'salesforce',
        'Salesforce',
        'https://www.salesforce.com',
        'Leading CRM platform for sales, service, and marketing',
        'crm',
        150.00,
        'USD',
        '["api", "mobile", "analytics", "automation", "ai"]'::jsonb,
        '["SOC2", "ISO27001", "GDPR", "HIPAA"]'::jsonb,
        4.5,
        1250,
        0.95
    ),
    (
        'hubspot',
        'HubSpot',
        'https://www.hubspot.com',
        'All-in-one CRM platform for marketing, sales, and service',
        'crm',
        120.00,
        'USD',
        '["api", "mobile", "marketing", "automation", "analytics"]'::jsonb,
        '["SOC2", "ISO27001", "GDPR"]'::jsonb,
        4.3,
        980,
        0.92
    ),
    (
        'slack',
        'Slack',
        'https://slack.com',
        'Team collaboration and messaging platform',
        'collaboration',
        8.00,
        'USD',
        '["api", "mobile", "integrations", "search", "channels"]'::jsonb,
        '["SOC2", "ISO27001", "GDPR"]'::jsonb,
        4.6,
        2100,
        0.98
    ),
    (
        'zoom',
        'Zoom',
        'https://zoom.us',
        'Video conferencing and collaboration platform',
        'collaboration',
        15.00,
        'USD',
        '["video", "webinar", "recording", "api", "mobile"]'::jsonb,
        '["SOC2", "ISO27001", "GDPR", "HIPAA"]'::jsonb,
        4.4,
        1800,
        0.96
    ),
    (
        'aws',
        'Amazon Web Services',
        'https://aws.amazon.com',
        'Cloud computing and infrastructure services',
        'cloud',
        0.10,
        'USD',
        '["compute", "storage", "database", "ai", "analytics"]'::jsonb,
        '["SOC2", "ISO27001", "GDPR", "HIPAA", "FedRAMP"]'::jsonb,
        4.7,
        3500,
        0.99
    )
ON CONFLICT (vendor_id) DO NOTHING;

-- =====================================================
-- SAMPLE PROCUREMENT REQUESTS
-- =====================================================

DO $$
DECLARE
    demo_buyer_id INTEGER;
    acme_admin_id INTEGER;
BEGIN
    -- Get user IDs
    SELECT id INTO STRICT demo_buyer_id FROM user_accounts WHERE email = 'buyer@demo-org.com';
    SELECT id INTO STRICT acme_admin_id FROM user_accounts WHERE email = 'admin@acme-corp.com';
    
    -- Insert sample requests
    INSERT INTO requests (
        request_id, user_id, description, request_type, category,
        budget_min, budget_max, quantity, billing_cadence,
        must_haves, nice_to_haves, compliance_requirements,
        status, procurement_goal, timeline_urgency
    )
    VALUES 
        (
            'req-001',
            demo_buyer_id,
            'Need a CRM system for our sales team of 50 people',
            'saas',
            'crm',
            5000.00,
            8000.00,
            50,
            'monthly',
            '["api_integration", "mobile_app", "reporting"]'::jsonb,
            '["ai_features", "custom_workflows"]'::jsonb,
            '["SOC2", "GDPR"]'::jsonb,
            'pending',
            'Improve sales team productivity and customer tracking',
            'high'
        ),
        (
            'req-002',
            demo_buyer_id,
            'Video conferencing solution for remote team',
            'saas',
            'collaboration',
            500.00,
            1500.00,
            100,
            'monthly',
            '["screen_sharing", "recording", "mobile_support"]'::jsonb,
            '["webinar_features", "breakout_rooms"]'::jsonb,
            '["SOC2"]'::jsonb,
            'approved',
            'Enable effective remote collaboration',
            'medium'
        ),
        (
            'req-003',
            acme_admin_id,
            'Cloud infrastructure for new application deployment',
            'infrastructure',
            'cloud',
            2000.00,
            5000.00,
            1,
            'monthly',
            '["auto_scaling", "load_balancing", "monitoring"]'::jsonb,
            '["managed_database", "cdn"]'::jsonb,
            '["SOC2", "ISO27001"]'::jsonb,
            'pending',
            'Deploy scalable application infrastructure',
            'critical'
        )
    ON CONFLICT (request_id) DO NOTHING;
END $$;

-- =====================================================
-- SAMPLE NEGOTIATION SESSIONS
-- =====================================================

DO $$
DECLARE
    req1_id INTEGER;
    req2_id INTEGER;
    salesforce_id INTEGER;
    hubspot_id INTEGER;
    zoom_id INTEGER;
    session1_id INTEGER;
    session2_id INTEGER;
BEGIN
    -- Get IDs
    SELECT id INTO STRICT req1_id FROM requests WHERE request_id = 'req-001';
    SELECT id INTO STRICT req2_id FROM requests WHERE request_id = 'req-002';
    SELECT id INTO STRICT salesforce_id FROM vendor_profiles WHERE vendor_id = 'salesforce';
    SELECT id INTO STRICT hubspot_id FROM vendor_profiles WHERE vendor_id = 'hubspot';
    SELECT id INTO STRICT zoom_id FROM vendor_profiles WHERE vendor_id = 'zoom';
    
    -- Insert negotiation sessions
    INSERT INTO negotiation_sessions (
        session_id, request_id, vendor_id, status, current_round, max_rounds,
        buyer_state, seller_state, started_at
    )
    VALUES 
        (
            'session-001',
            req1_id,
            salesforce_id,
            'active',
            2,
            8,
            '{"target_price": 140, "max_price": 150, "strategy": "collaborative"}'::jsonb,
            '{"min_price": 135, "target_price": 145, "strategy": "value_based"}'::jsonb,
            NOW() - INTERVAL '2 hours'
        ),
        (
            'session-002',
            req1_id,
            hubspot_id,
            'completed',
            5,
            8,
            '{"target_price": 110, "max_price": 120, "strategy": "competitive"}'::jsonb,
            '{"min_price": 105, "target_price": 115, "strategy": "competitive"}'::jsonb,
            NOW() - INTERVAL '1 day'
        ),
        (
            'session-003',
            req2_id,
            zoom_id,
            'active',
            1,
            8,
            '{"target_price": 12, "max_price": 15, "strategy": "collaborative"}'::jsonb,
            '{"min_price": 13, "target_price": 14, "strategy": "value_based"}'::jsonb,
            NOW() - INTERVAL '30 minutes'
        )
    ON CONFLICT (request_id, vendor_id) DO NOTHING
    RETURNING id INTO session1_id;
    
    -- Get session IDs for offers
    SELECT id INTO STRICT session1_id FROM negotiation_sessions WHERE session_id = 'session-001';
    SELECT id INTO STRICT session2_id FROM negotiation_sessions WHERE session_id = 'session-002';
END $$;

-- =====================================================
-- SAMPLE OFFERS
-- =====================================================

DO $$
DECLARE
    req1_id INTEGER;
    req2_id INTEGER;
    salesforce_id INTEGER;
    hubspot_id INTEGER;
    zoom_id INTEGER;
    session1_id INTEGER;
    session2_id INTEGER;
    session3_id INTEGER;
BEGIN
    -- Get IDs
    SELECT id INTO STRICT req1_id FROM requests WHERE request_id = 'req-001';
    SELECT id INTO STRICT req2_id FROM requests WHERE request_id = 'req-002';
    SELECT id INTO STRICT salesforce_id FROM vendor_profiles WHERE vendor_id = 'salesforce';
    SELECT id INTO STRICT hubspot_id FROM vendor_profiles WHERE vendor_id = 'hubspot';
    SELECT id INTO STRICT zoom_id FROM vendor_profiles WHERE vendor_id = 'zoom';
    SELECT id INTO STRICT session1_id FROM negotiation_sessions WHERE session_id = 'session-001';
    SELECT id INTO STRICT session2_id FROM negotiation_sessions WHERE session_id = 'session-002';
    SELECT id INTO STRICT session3_id FROM negotiation_sessions WHERE session_id = 'session-003';
    
    -- Insert sample offers
    INSERT INTO offers (
        offer_id, request_id, vendor_id, negotiation_session_id,
        unit_price, quantity, term_months, payment_terms, currency,
        discount_percent, value_adds, score, utility_buyer, utility_seller,
        accepted, rejected, round_number, actor, strategy
    )
    VALUES 
        -- Salesforce negotiation - Round 1
        (
            'offer-001',
            req1_id,
            salesforce_id,
            session1_id,
            150.00,
            50,
            12,
            'NET30',
            'USD',
            0,
            '["onboarding", "training"]'::jsonb,
            85.5,
            0.75,
            0.95,
            false,
            false,
            1,
            'seller',
            'value_based'
        ),
        -- Salesforce negotiation - Round 2 (current)
        (
            'offer-002',
            req1_id,
            salesforce_id,
            session1_id,
            142.00,
            50,
            12,
            'NET30',
            'USD',
            5.3,
            '["onboarding", "training", "priority_support"]'::jsonb,
            88.2,
            0.82,
            0.88,
            false,
            false,
            2,
            'seller',
            'collaborative'
        ),
        -- HubSpot negotiation - Final accepted offer
        (
            'offer-003',
            req1_id,
            hubspot_id,
            session2_id,
            112.00,
            50,
            12,
            'NET30',
            'USD',
            6.7,
            '["onboarding", "training", "api_credits"]'::jsonb,
            92.5,
            0.90,
            0.85,
            true,
            false,
            5,
            'seller',
            'competitive'
        ),
        -- Zoom negotiation - Initial offer
        (
            'offer-004',
            req2_id,
            zoom_id,
            session3_id,
            15.00,
            100,
            12,
            'NET30',
            'USD',
            0,
            '["onboarding"]'::jsonb,
            80.0,
            0.70,
            0.95,
            false,
            false,
            1,
            'seller',
            'value_based'
        )
    ON CONFLICT (offer_id) DO NOTHING;
END $$;

-- =====================================================
-- SAMPLE NEGOTIATION EVENTS
-- =====================================================

INSERT INTO negotiation_events (session_id, event_type, event_data)
VALUES 
    (
        'session-001',
        'session_started',
        '{"actor": "system", "timestamp": "2025-10-07T17:00:00Z", "details": "Negotiation session initiated"}'::jsonb
    ),
    (
        'session-001',
        'offer_made',
        '{"actor": "seller", "offer_id": "offer-001", "round": 1, "price": 150.00}'::jsonb
    ),
    (
        'session-001',
        'offer_countered',
        '{"actor": "buyer", "round": 2, "requested_price": 140.00}'::jsonb
    ),
    (
        'session-001',
        'offer_made',
        '{"actor": "seller", "offer_id": "offer-002", "round": 2, "price": 142.00}'::jsonb
    ),
    (
        'session-002',
        'session_started',
        '{"actor": "system", "timestamp": "2025-10-06T10:00:00Z", "details": "Negotiation session initiated"}'::jsonb
    ),
    (
        'session-002',
        'offer_accepted',
        '{"actor": "buyer", "offer_id": "offer-003", "round": 5, "final_price": 112.00}'::jsonb
    ),
    (
        'session-002',
        'session_completed',
        '{"actor": "system", "outcome": "accepted", "savings": 400.00}'::jsonb
    )
ON CONFLICT DO NOTHING;

-- =====================================================
-- SAMPLE POLICY CONFIGS
-- =====================================================

DO $$
DECLARE
    demo_admin_id INTEGER;
BEGIN
    SELECT id INTO STRICT demo_admin_id FROM user_accounts WHERE email = 'admin@demo-org.com';
    
    INSERT INTO policy_configs (
        policy_name, policy_type, organization_id, policy_data,
        version, is_active, description, created_by
    )
    VALUES 
        (
            'budget_approval_policy',
            'approval',
            'demo-org',
            '{
                "rules": [
                    {"threshold": 5000, "approvers": 1, "roles": ["approver"]},
                    {"threshold": 25000, "approvers": 2, "roles": ["approver", "admin"]},
                    {"threshold": 100000, "approvers": 3, "roles": ["admin"]}
                ]
            }'::jsonb,
            1,
            true,
            'Budget approval thresholds and required approvers',
            demo_admin_id
        ),
        (
            'compliance_policy',
            'compliance',
            'demo-org',
            '{
                "required_certifications": ["SOC2", "GDPR"],
                "optional_certifications": ["ISO27001", "HIPAA"],
                "data_residency": ["US", "EU"]
            }'::jsonb,
            1,
            true,
            'Compliance requirements for vendor selection',
            demo_admin_id
        ),
        (
            'negotiation_policy',
            'negotiation',
            'demo-org',
            '{
                "max_rounds": 8,
                "min_discount_target": 5,
                "auto_accept_threshold": 95,
                "strategies": ["collaborative", "competitive", "value_based"]
            }'::jsonb,
            1,
            true,
            'Negotiation parameters and strategies',
            demo_admin_id
        )
    ON CONFLICT (policy_name, organization_id, version) DO NOTHING;
END $$;

-- =====================================================
-- SAMPLE AUDIT LOGS
-- =====================================================

DO $$
DECLARE
    demo_buyer_id INTEGER;
    demo_admin_id INTEGER;
BEGIN
    SELECT id INTO STRICT demo_buyer_id FROM user_accounts WHERE email = 'buyer@demo-org.com';
    SELECT id INTO STRICT demo_admin_id FROM user_accounts WHERE email = 'admin@demo-org.com';
    
    INSERT INTO audit_logs (
        user_id, actor_type, action, resource_type, resource_id,
        event_data, ip_address
    )
    VALUES 
        (
            demo_buyer_id,
            'user',
            'create_request',
            'request',
            'req-001',
            '{"category": "crm", "budget_max": 8000}'::jsonb,
            '192.168.1.100'
        ),
        (
            demo_admin_id,
            'user',
            'approve_request',
            'request',
            'req-002',
            '{"approved": true, "notes": "Approved for Q4 budget"}'::jsonb,
            '192.168.1.101'
        ),
        (
            NULL,
            'system',
            'start_negotiation',
            'negotiation_session',
            'session-001',
            '{"vendor": "salesforce", "request": "req-001"}'::jsonb,
            NULL
        )
    ON CONFLICT DO NOTHING;
END $$;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check what was created
DO $$
BEGIN
    RAISE NOTICE 'Sample data seeded successfully!';
    RAISE NOTICE 'Organizations: %', (SELECT COUNT(*) FROM organizations);
    RAISE NOTICE 'Users: %', (SELECT COUNT(*) FROM user_accounts);
    RAISE NOTICE 'Vendors: %', (SELECT COUNT(*) FROM vendor_profiles);
    RAISE NOTICE 'Requests: %', (SELECT COUNT(*) FROM requests);
    RAISE NOTICE 'Negotiation Sessions: %', (SELECT COUNT(*) FROM negotiation_sessions);
    RAISE NOTICE 'Offers: %', (SELECT COUNT(*) FROM offers);
    RAISE NOTICE 'Negotiation Events: %', (SELECT COUNT(*) FROM negotiation_events);
    RAISE NOTICE 'Policy Configs: %', (SELECT COUNT(*) FROM policy_configs);
    RAISE NOTICE 'Audit Logs: %', (SELECT COUNT(*) FROM audit_logs);
END $$;

-- =====================================================
-- End of seed data
-- =====================================================

-- NOTE: Default password for all test users is 'password123'
-- Change these passwords immediately in production!
