#!/usr/bin/env python3
"""Generate initial Alembic migration without requiring database connection."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from alembic import command
from alembic.config import Config

def generate_initial_migration():
    """Generate initial migration file manually."""
    
    # Create migration file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    revision_id = timestamp[:12]
    
    migration_content = f'''"""initial_schema

Revision ID: {revision_id}
Revises: 
Create Date: {datetime.utcnow().isoformat()}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for Procur platform."""
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('billing_email', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )
    op.create_index('ix_organizations_organization_id', 'organizations', ['organization_id'])
    op.create_index('ix_organizations_name', 'organizations', ['name'])
    
    # Create user_accounts table
    op.create_table(
        'user_accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('organization_id', sa.String(length=100), nullable=True),
        sa.Column('team', sa.String(length=100), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(), nullable=False),
        sa.Column('password_expires_at', sa.DateTime(), nullable=True),
        sa.Column('must_change_password', sa.Boolean(), nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('email_verification_token', sa.String(length=100), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False),
        sa.Column('mfa_secret', sa.String(length=100), nullable=True),
        sa.Column('mfa_backup_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_password_change_at', sa.DateTime(), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_user_accounts_email', 'user_accounts', ['email'])
    op.create_index('ix_user_accounts_username', 'user_accounts', ['username'])
    op.create_index('ix_user_accounts_organization_id', 'user_accounts', ['organization_id'])
    
    # Create requests table
    op.create_table(
        'requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('budget_min', sa.Float(), nullable=True),
        sa.Column('budget_max', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('billing_cadence', sa.String(length=50), nullable=True),
        sa.Column('must_haves', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('nice_to_haves', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_requirements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('specs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_accounts.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )
    op.create_index('ix_requests_request_id', 'requests', ['request_id'])
    op.create_index('ix_requests_category', 'requests', ['category'])
    op.create_index('ix_requests_status', 'requests', ['status'])
    
    # Create vendor_profiles table
    op.create_table(
        'vendor_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('list_price', sa.Float(), nullable=True),
        sa.Column('price_tiers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('integrations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('certifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_frameworks', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('guardrails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('exchange_policy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('vendor_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(length=100), nullable=True),
        sa.Column('last_enriched_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_id')
    )
    op.create_index('ix_vendor_profiles_vendor_id', 'vendor_profiles', ['vendor_id'])
    op.create_index('ix_vendor_profiles_name', 'vendor_profiles', ['name'])
    op.create_index('ix_vendor_profiles_category', 'vendor_profiles', ['category'])
    
    # Create offers table
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('offer_id', sa.String(length=100), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('contract_term_months', sa.Integer(), nullable=True),
        sa.Column('payment_terms', sa.String(length=50), nullable=True),
        sa.Column('discount_percentage', sa.Float(), nullable=True),
        sa.Column('features_included', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('features_excluded', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_met', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_gaps', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tco', sa.Float(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('offer_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('offer_id')
    )
    op.create_index('ix_offers_offer_id', 'offers', ['offer_id'])
    op.create_index('ix_offers_status', 'offers', ['status'])
    
    # Create contracts table
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.String(length=100), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('auto_renew', sa.Boolean(), nullable=False),
        sa.Column('renewal_notice_days', sa.Integer(), nullable=True),
        sa.Column('payment_schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('sla_terms', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=True),
        sa.Column('signed_by', sa.Integer(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('contract_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_profiles.id']),
        sa.ForeignKeyConstraint(['offer_id'], ['offers.id']),
        sa.ForeignKeyConstraint(['signed_by'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_id')
    )
    op.create_index('ix_contracts_contract_id', 'contracts', ['contract_id'])
    op.create_index('ix_contracts_status', 'contracts', ['status'])
    
    # Create negotiation_sessions table
    op.create_table(
        'negotiation_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_round', sa.Integer(), nullable=False),
        sa.Column('max_rounds', sa.Integer(), nullable=False),
        sa.Column('buyer_strategy', sa.String(length=50), nullable=True),
        sa.Column('seller_strategy', sa.String(length=50), nullable=True),
        sa.Column('opponent_model', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('final_offer_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('session_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_profiles.id']),
        sa.ForeignKeyConstraint(['final_offer_id'], ['offers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('ix_negotiation_sessions_session_id', 'negotiation_sessions', ['session_id'])
    op.create_index('ix_negotiation_sessions_status', 'negotiation_sessions', ['status'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('log_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('changes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('log_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('log_id')
    )
    op.create_index('ix_audit_logs_log_id', 'audit_logs', ['log_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    
    # Create policy_configs table
    op.create_table(
        'policy_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('policy_id', sa.String(length=100), nullable=False),
        sa.Column('organization_id', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('policy_type', sa.String(length=50), nullable=False),
        sa.Column('rules', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('policy_id')
    )
    op.create_index('ix_policy_configs_policy_id', 'policy_configs', ['policy_id'])
    op.create_index('ix_policy_configs_organization_id', 'policy_configs', ['organization_id'])
    
    # Create authentication tables
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.String(length=200), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('ix_user_sessions_session_id', 'user_sessions', ['session_id'])
    
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('key_prefix', sa.String(length=20), nullable=False),
        sa.Column('scopes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_id')
    )
    op.create_index('ix_api_keys_key_id', 'api_keys', ['key_id'])
    op.create_index('ix_api_keys_key_prefix', 'api_keys', ['key_prefix'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('api_keys')
    op.drop_table('user_sessions')
    op.drop_table('policy_configs')
    op.drop_table('audit_logs')
    op.drop_table('negotiation_sessions')
    op.drop_table('contracts')
    op.drop_table('offers')
    op.drop_table('vendor_profiles')
    op.drop_table('requests')
    op.drop_table('user_accounts')
    op.drop_table('organizations')
'''
    
    # Write migration file
    versions_dir = project_root / "alembic" / "versions"
    versions_dir.mkdir(exist_ok=True)
    
    migration_file = versions_dir / f"{revision_id}_initial_schema.py"
    migration_file.write_text(migration_content)
    
    print(f"✅ Created migration: {migration_file.name}")
    print(f"   Revision ID: {revision_id}")
    print("\nNext steps:")
    print("  1. Setup database: bash scripts/setup_database.sh")
    print("  2. Run migration: alembic upgrade head")

if __name__ == "__main__":
    generate_initial_migration()
