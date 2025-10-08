-- =====================================================
-- Procur Platform - Supabase Schema Migration
-- File: 03_create_triggers.sql
-- Description: Create triggers for automatic timestamp updates
-- =====================================================

-- =====================================================
-- FUNCTION: update_updated_at_column
-- Automatically update updated_at timestamp
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Trigger function to automatically update updated_at timestamp';

-- =====================================================
-- TRIGGERS: Apply updated_at to all tables
-- =====================================================

-- organizations
CREATE TRIGGER trigger_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- user_accounts
CREATE TRIGGER trigger_user_accounts_updated_at
    BEFORE UPDATE ON user_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- user_sessions
CREATE TRIGGER trigger_user_sessions_updated_at
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- api_keys
CREATE TRIGGER trigger_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- password_history
CREATE TRIGGER trigger_password_history_updated_at
    BEFORE UPDATE ON password_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- login_attempts
CREATE TRIGGER trigger_login_attempts_updated_at
    BEFORE UPDATE ON login_attempts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- oauth_connections
CREATE TRIGGER trigger_oauth_connections_updated_at
    BEFORE UPDATE ON oauth_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- requests
CREATE TRIGGER trigger_requests_updated_at
    BEFORE UPDATE ON requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- vendor_profiles
CREATE TRIGGER trigger_vendor_profiles_updated_at
    BEFORE UPDATE ON vendor_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- negotiation_sessions
CREATE TRIGGER trigger_negotiation_sessions_updated_at
    BEFORE UPDATE ON negotiation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- offers
CREATE TRIGGER trigger_offers_updated_at
    BEFORE UPDATE ON offers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- contracts
CREATE TRIGGER trigger_contracts_updated_at
    BEFORE UPDATE ON contracts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- negotiation_events
CREATE TRIGGER trigger_negotiation_events_updated_at
    BEFORE UPDATE ON negotiation_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- audit_logs
CREATE TRIGGER trigger_audit_logs_updated_at
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- policy_configs
CREATE TRIGGER trigger_policy_configs_updated_at
    BEFORE UPDATE ON policy_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNCTION: log_audit_event
-- Automatically log changes to audit_logs
-- =====================================================

CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS TRIGGER AS $$
DECLARE
    v_action VARCHAR(100);
    v_changes JSONB;
BEGIN
    -- Determine action type
    IF (TG_OP = 'DELETE') THEN
        v_action := 'delete_' || TG_TABLE_NAME;
        v_changes := to_jsonb(OLD);
    ELSIF (TG_OP = 'UPDATE') THEN
        v_action := 'update_' || TG_TABLE_NAME;
        v_changes := jsonb_build_object(
            'before', to_jsonb(OLD),
            'after', to_jsonb(NEW)
        );
    ELSIF (TG_OP = 'INSERT') THEN
        v_action := 'create_' || TG_TABLE_NAME;
        v_changes := to_jsonb(NEW);
    END IF;

    -- Insert audit log
    INSERT INTO audit_logs (
        actor_type,
        action,
        resource_type,
        resource_id,
        changes,
        created_at,
        updated_at
    ) VALUES (
        'system',
        v_action,
        TG_TABLE_NAME,
        COALESCE(NEW.id::TEXT, OLD.id::TEXT),
        v_changes,
        NOW(),
        NOW()
    );

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION log_audit_event() IS 'Trigger function to automatically log changes to audit_logs table';

-- =====================================================
-- FUNCTION: increment_api_key_usage
-- Increment usage count when API key is used
-- =====================================================

CREATE OR REPLACE FUNCTION increment_api_key_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE api_keys
    SET 
        usage_count = usage_count + 1,
        last_used_at = NOW()
    WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION increment_api_key_usage() IS 'Increment API key usage count and update last_used_at';

-- =====================================================
-- FUNCTION: update_session_activity
-- Update last_activity_at on session access
-- =====================================================

CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_session_activity() IS 'Update session last_activity_at timestamp';

CREATE TRIGGER trigger_user_sessions_activity
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    WHEN (OLD.last_activity_at IS DISTINCT FROM NEW.last_activity_at)
    EXECUTE FUNCTION update_session_activity();

-- =====================================================
-- FUNCTION: validate_contract_dates
-- Ensure contract dates are logical
-- =====================================================

CREATE OR REPLACE FUNCTION validate_contract_dates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.end_date IS NOT NULL AND NEW.start_date IS NOT NULL THEN
        IF NEW.end_date <= NEW.start_date THEN
            RAISE EXCEPTION 'Contract end_date must be after start_date';
        END IF;
    END IF;
    
    IF NEW.renewal_date IS NOT NULL AND NEW.end_date IS NOT NULL THEN
        IF NEW.renewal_date > NEW.end_date THEN
            RAISE EXCEPTION 'Contract renewal_date must be before or equal to end_date';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_contract_dates() IS 'Validate contract date logic';

CREATE TRIGGER trigger_contracts_validate_dates
    BEFORE INSERT OR UPDATE ON contracts
    FOR EACH ROW
    EXECUTE FUNCTION validate_contract_dates();

-- =====================================================
-- FUNCTION: calculate_contract_total_value
-- Automatically calculate total contract value
-- =====================================================

CREATE OR REPLACE FUNCTION calculate_contract_total_value()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_value = NEW.unit_price * NEW.quantity * NEW.term_months;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_contract_total_value() IS 'Automatically calculate contract total_value';

CREATE TRIGGER trigger_contracts_calculate_total
    BEFORE INSERT OR UPDATE ON contracts
    FOR EACH ROW
    WHEN (NEW.unit_price IS NOT NULL AND NEW.quantity IS NOT NULL AND NEW.term_months IS NOT NULL)
    EXECUTE FUNCTION calculate_contract_total_value();

-- =====================================================
-- FUNCTION: prevent_audit_log_modification
-- Prevent modification or deletion of audit logs
-- =====================================================

CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION prevent_audit_log_modification() IS 'Prevent modification or deletion of audit logs';

CREATE TRIGGER trigger_audit_logs_prevent_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_log_modification();

CREATE TRIGGER trigger_audit_logs_prevent_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_log_modification();

-- =====================================================
-- FUNCTION: increment_negotiation_round
-- Increment negotiation round when new offer is created
-- =====================================================

CREATE OR REPLACE FUNCTION increment_negotiation_round()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment total_messages in negotiation session
    UPDATE negotiation_sessions
    SET total_messages = total_messages + 1
    WHERE id = NEW.negotiation_session_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION increment_negotiation_round() IS 'Increment negotiation session message count';

CREATE TRIGGER trigger_offers_increment_round
    AFTER INSERT ON offers
    FOR EACH ROW
    WHEN (NEW.negotiation_session_id IS NOT NULL)
    EXECUTE FUNCTION increment_negotiation_round();

-- =====================================================
-- FUNCTION: update_user_last_login
-- Update user last_login_at on successful login
-- =====================================================

CREATE OR REPLACE FUNCTION update_user_last_login()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.success = true THEN
        UPDATE user_accounts
        SET last_login_at = NOW()
        WHERE id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_user_last_login() IS 'Update user last_login_at on successful login';

CREATE TRIGGER trigger_login_attempts_update_last_login
    AFTER INSERT ON login_attempts
    FOR EACH ROW
    WHEN (NEW.success = true AND NEW.user_id IS NOT NULL)
    EXECUTE FUNCTION update_user_last_login();

-- =====================================================
-- End of trigger creation
-- =====================================================
