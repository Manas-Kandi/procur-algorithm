-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 05_create_functions.sql
-- Description: Helper functions and stored procedures
-- =====================================================

-- =====================================================
-- FUNCTION: get_active_negotiations_count
-- Get count of active negotiations for an organization
-- =====================================================

CREATE OR REPLACE FUNCTION get_active_negotiations_count(org_id VARCHAR)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM negotiation_sessions ns
        JOIN requests r ON ns.request_id = r.id
        JOIN user_accounts u ON r.user_id = u.id
        WHERE u.organization_id = org_id
        AND ns.status = 'active'
        AND ns.deleted_at IS NULL
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_active_negotiations_count(VARCHAR) IS 'Get count of active negotiations for an organization';

-- =====================================================
-- FUNCTION: get_request_pipeline_stats
-- Get request pipeline statistics for an organization
-- =====================================================

CREATE OR REPLACE FUNCTION get_request_pipeline_stats(org_id VARCHAR)
RETURNS TABLE(
    status VARCHAR,
    count BIGINT,
    total_budget NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.status,
        COUNT(*)::BIGINT,
        SUM(r.budget_max)
    FROM requests r
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id
    AND r.deleted_at IS NULL
    GROUP BY r.status;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_request_pipeline_stats(VARCHAR) IS 'Get request pipeline statistics by status';

-- =====================================================
-- FUNCTION: get_vendor_performance
-- Get vendor performance metrics
-- =====================================================

CREATE OR REPLACE FUNCTION get_vendor_performance(v_id INTEGER)
RETURNS TABLE(
    vendor_name VARCHAR,
    total_negotiations BIGINT,
    successful_negotiations BIGINT,
    avg_savings NUMERIC,
    avg_rounds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vp.name,
        COUNT(DISTINCT ns.id)::BIGINT,
        COUNT(DISTINCT CASE WHEN ns.outcome = 'accepted' THEN ns.id END)::BIGINT,
        AVG(ns.savings_achieved),
        AVG(ns.current_round)
    FROM vendor_profiles vp
    LEFT JOIN negotiation_sessions ns ON vp.id = ns.vendor_id
    WHERE vp.id = v_id
    GROUP BY vp.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_vendor_performance(INTEGER) IS 'Get performance metrics for a vendor';

-- =====================================================
-- FUNCTION: search_vendors
-- Full-text search for vendors
-- =====================================================

CREATE OR REPLACE FUNCTION search_vendors(
    search_term VARCHAR,
    search_category VARCHAR DEFAULT NULL,
    min_rating NUMERIC DEFAULT 0
)
RETURNS TABLE(
    id INTEGER,
    vendor_id VARCHAR,
    name VARCHAR,
    category VARCHAR,
    rating NUMERIC,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vp.id,
        vp.vendor_id,
        vp.name,
        vp.category,
        vp.rating,
        similarity(vp.name, search_term) as sim
    FROM vendor_profiles vp
    WHERE 
        vp.deleted_at IS NULL
        AND (search_category IS NULL OR vp.category = search_category)
        AND (vp.rating IS NULL OR vp.rating >= min_rating)
        AND (
            vp.name ILIKE '%' || search_term || '%'
            OR vp.description ILIKE '%' || search_term || '%'
            OR similarity(vp.name, search_term) > 0.3
        )
    ORDER BY sim DESC, vp.rating DESC NULLS LAST
    LIMIT 50;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION search_vendors(VARCHAR, VARCHAR, NUMERIC) IS 'Full-text search for vendors with similarity ranking';

-- =====================================================
-- FUNCTION: get_negotiation_timeline
-- Get timeline of events for a negotiation session
-- =====================================================

CREATE OR REPLACE FUNCTION get_negotiation_timeline(session_id_param VARCHAR)
RETURNS TABLE(
    event_id INTEGER,
    event_type VARCHAR,
    event_time TIMESTAMP,
    actor VARCHAR,
    details JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ne.id,
        ne.event_type,
        ne.created_at,
        (ne.event_data->>'actor')::VARCHAR,
        ne.event_data
    FROM negotiation_events ne
    WHERE ne.session_id = session_id_param
    ORDER BY ne.created_at ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_negotiation_timeline(VARCHAR) IS 'Get chronological timeline of negotiation events';

-- =====================================================
-- FUNCTION: calculate_savings
-- Calculate savings achieved in a negotiation
-- =====================================================

CREATE OR REPLACE FUNCTION calculate_savings(
    initial_price NUMERIC,
    final_price NUMERIC,
    quantity INTEGER,
    term_months INTEGER
)
RETURNS NUMERIC AS $$
BEGIN
    RETURN (initial_price - final_price) * quantity * term_months;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_savings(NUMERIC, NUMERIC, INTEGER, INTEGER) IS 'Calculate total savings from price negotiation';

-- =====================================================
-- FUNCTION: get_expiring_contracts
-- Get contracts expiring within specified days
-- =====================================================

CREATE OR REPLACE FUNCTION get_expiring_contracts(
    org_id VARCHAR,
    days_ahead INTEGER DEFAULT 90
)
RETURNS TABLE(
    contract_id VARCHAR,
    vendor_name VARCHAR,
    end_date TIMESTAMP,
    days_until_expiry INTEGER,
    total_value NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.contract_id,
        vp.name,
        c.end_date,
        EXTRACT(DAY FROM (c.end_date - NOW()))::INTEGER,
        c.total_value
    FROM contracts c
    JOIN vendor_profiles vp ON c.vendor_id = vp.id
    JOIN requests r ON c.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE 
        u.organization_id = org_id
        AND c.status = 'active'
        AND c.end_date IS NOT NULL
        AND c.end_date BETWEEN NOW() AND NOW() + (days_ahead || ' days')::INTERVAL
        AND c.deleted_at IS NULL
    ORDER BY c.end_date ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_expiring_contracts(VARCHAR, INTEGER) IS 'Get contracts expiring within specified days';

-- =====================================================
-- FUNCTION: get_user_activity_summary
-- Get activity summary for a user
-- =====================================================

CREATE OR REPLACE FUNCTION get_user_activity_summary(user_id_param INTEGER)
RETURNS TABLE(
    total_requests BIGINT,
    active_negotiations BIGINT,
    completed_contracts BIGINT,
    total_savings NUMERIC,
    avg_negotiation_rounds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT r.id)::BIGINT,
        COUNT(DISTINCT CASE WHEN ns.status = 'active' THEN ns.id END)::BIGINT,
        COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END)::BIGINT,
        SUM(ns.savings_achieved),
        AVG(ns.current_round)
    FROM user_accounts u
    LEFT JOIN requests r ON u.id = r.user_id AND r.deleted_at IS NULL
    LEFT JOIN negotiation_sessions ns ON r.id = ns.request_id AND ns.deleted_at IS NULL
    LEFT JOIN contracts c ON r.id = c.request_id AND c.deleted_at IS NULL
    WHERE u.id = user_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_user_activity_summary(INTEGER) IS 'Get activity summary for a user';

-- =====================================================
-- FUNCTION: get_top_vendors_by_savings
-- Get top vendors by total savings achieved
-- =====================================================

CREATE OR REPLACE FUNCTION get_top_vendors_by_savings(
    org_id VARCHAR,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE(
    vendor_id VARCHAR,
    vendor_name VARCHAR,
    total_savings NUMERIC,
    negotiation_count BIGINT,
    avg_savings_per_deal NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vp.vendor_id,
        vp.name,
        SUM(ns.savings_achieved),
        COUNT(ns.id)::BIGINT,
        AVG(ns.savings_achieved)
    FROM vendor_profiles vp
    JOIN negotiation_sessions ns ON vp.id = ns.vendor_id
    JOIN requests r ON ns.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE 
        u.organization_id = org_id
        AND ns.outcome = 'accepted'
        AND ns.savings_achieved IS NOT NULL
        AND ns.deleted_at IS NULL
    GROUP BY vp.vendor_id, vp.name
    ORDER BY SUM(ns.savings_achieved) DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_top_vendors_by_savings(VARCHAR, INTEGER) IS 'Get top vendors by total savings achieved';

-- =====================================================
-- FUNCTION: validate_offer_terms
-- Validate offer terms against request requirements
-- =====================================================

CREATE OR REPLACE FUNCTION validate_offer_terms(
    offer_id_param INTEGER
)
RETURNS TABLE(
    is_valid BOOLEAN,
    validation_errors TEXT[]
) AS $$
DECLARE
    v_errors TEXT[] := ARRAY[]::TEXT[];
    v_offer RECORD;
    v_request RECORD;
BEGIN
    -- Get offer and request details
    SELECT o.*, r.budget_max, r.quantity as req_quantity
    INTO v_offer
    FROM offers o
    JOIN requests r ON o.request_id = r.id
    WHERE o.id = offer_id_param;
    
    -- Validate budget
    IF v_offer.unit_price * v_offer.quantity * v_offer.term_months > v_offer.budget_max THEN
        v_errors := array_append(v_errors, 'Total cost exceeds budget');
    END IF;
    
    -- Validate quantity
    IF v_offer.quantity < v_offer.req_quantity THEN
        v_errors := array_append(v_errors, 'Quantity is less than requested');
    END IF;
    
    -- Validate payment terms
    IF v_offer.payment_terms NOT IN ('NET30', 'NET15', 'NET60', 'upfront', 'monthly') THEN
        v_errors := array_append(v_errors, 'Invalid payment terms');
    END IF;
    
    RETURN QUERY SELECT (array_length(v_errors, 1) IS NULL), v_errors;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION validate_offer_terms(INTEGER) IS 'Validate offer terms against request requirements';

-- =====================================================
-- FUNCTION: get_compliance_status
-- Get compliance status for a request
-- =====================================================

CREATE OR REPLACE FUNCTION get_compliance_status(request_id_param INTEGER)
RETURNS TABLE(
    requirement VARCHAR,
    status VARCHAR,
    details JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        req::VARCHAR,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM offers o
                WHERE o.request_id = request_id_param
                AND o.conditions ? req
            ) THEN 'met'
            ELSE 'pending'
        END,
        jsonb_build_object('requirement', req)
    FROM requests r,
    jsonb_array_elements_text(r.compliance_requirements) req
    WHERE r.id = request_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_compliance_status(INTEGER) IS 'Get compliance status for request requirements';

-- =====================================================
-- FUNCTION: archive_old_sessions
-- Archive completed negotiation sessions older than specified days
-- =====================================================

CREATE OR REPLACE FUNCTION archive_old_sessions(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    WITH archived AS (
        UPDATE negotiation_sessions
        SET deleted_at = NOW()
        WHERE 
            status IN ('completed', 'failed', 'cancelled')
            AND completed_at < NOW() - (days_old || ' days')::INTERVAL
            AND deleted_at IS NULL
        RETURNING id
    )
    SELECT COUNT(*) INTO archived_count FROM archived;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION archive_old_sessions(INTEGER) IS 'Soft delete completed negotiation sessions older than specified days';

-- =====================================================
-- FUNCTION: get_organization_metrics
-- Get comprehensive metrics for an organization
-- =====================================================

CREATE OR REPLACE FUNCTION get_organization_metrics(org_id VARCHAR)
RETURNS TABLE(
    metric_name VARCHAR,
    metric_value NUMERIC,
    metric_unit VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    -- Total users
    SELECT 'total_users'::VARCHAR, COUNT(*)::NUMERIC, 'count'::VARCHAR
    FROM user_accounts WHERE organization_id = org_id AND deleted_at IS NULL
    
    UNION ALL
    
    -- Total requests
    SELECT 'total_requests'::VARCHAR, COUNT(*)::NUMERIC, 'count'::VARCHAR
    FROM requests r
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id AND r.deleted_at IS NULL
    
    UNION ALL
    
    -- Active negotiations
    SELECT 'active_negotiations'::VARCHAR, COUNT(*)::NUMERIC, 'count'::VARCHAR
    FROM negotiation_sessions ns
    JOIN requests r ON ns.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id AND ns.status = 'active' AND ns.deleted_at IS NULL
    
    UNION ALL
    
    -- Total savings
    SELECT 'total_savings'::VARCHAR, COALESCE(SUM(ns.savings_achieved), 0), 'currency'::VARCHAR
    FROM negotiation_sessions ns
    JOIN requests r ON ns.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id AND ns.deleted_at IS NULL
    
    UNION ALL
    
    -- Active contracts
    SELECT 'active_contracts'::VARCHAR, COUNT(*)::NUMERIC, 'count'::VARCHAR
    FROM contracts c
    JOIN requests r ON c.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id AND c.status = 'active' AND c.deleted_at IS NULL
    
    UNION ALL
    
    -- Total contract value
    SELECT 'total_contract_value'::VARCHAR, COALESCE(SUM(c.total_value), 0), 'currency'::VARCHAR
    FROM contracts c
    JOIN requests r ON c.request_id = r.id
    JOIN user_accounts u ON r.user_id = u.id
    WHERE u.organization_id = org_id AND c.status = 'active' AND c.deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_organization_metrics(VARCHAR) IS 'Get comprehensive metrics for an organization';

-- =====================================================
-- FUNCTION: cleanup_expired_sessions
-- Clean up expired user sessions
-- =====================================================

CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM user_sessions
        WHERE 
            expires_at < NOW()
            OR (is_active = false AND last_activity_at < NOW() - INTERVAL '30 days')
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cleanup_expired_sessions() IS 'Delete expired and inactive user sessions';

-- =====================================================
-- FUNCTION: get_negotiation_analytics
-- Get detailed analytics for a negotiation session
-- =====================================================

CREATE OR REPLACE FUNCTION get_negotiation_analytics(session_id_param VARCHAR)
RETURNS TABLE(
    session_id VARCHAR,
    status VARCHAR,
    total_rounds INTEGER,
    total_offers INTEGER,
    initial_price NUMERIC,
    final_price NUMERIC,
    price_reduction_percent NUMERIC,
    duration_hours NUMERIC,
    outcome VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ns.session_id,
        ns.status,
        ns.current_round,
        COUNT(o.id)::INTEGER,
        MIN(o.unit_price),
        MAX(CASE WHEN o.accepted = true THEN o.unit_price END),
        CASE 
            WHEN MIN(o.unit_price) > 0 THEN
                ((MIN(o.unit_price) - MAX(CASE WHEN o.accepted = true THEN o.unit_price END)) / MIN(o.unit_price) * 100)
            ELSE 0
        END,
        EXTRACT(EPOCH FROM (COALESCE(ns.completed_at, NOW()) - ns.started_at)) / 3600,
        ns.outcome
    FROM negotiation_sessions ns
    LEFT JOIN offers o ON ns.id = o.negotiation_session_id
    WHERE ns.session_id = session_id_param
    GROUP BY ns.session_id, ns.status, ns.current_round, ns.started_at, ns.completed_at, ns.outcome;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_negotiation_analytics(VARCHAR) IS 'Get detailed analytics for a negotiation session';

-- =====================================================
-- End of helper functions
-- =====================================================
