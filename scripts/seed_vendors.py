#!/usr/bin/env python3
"""Seed vendors and test users from seeds.json for frontend-backend integration testing."""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.procur.api.security import get_password_hash
from src.procur.db.models import UserAccount, VendorProfileRecord, Organization
from src.procur.db.session import session_context


def load_seed_data():
    """Load vendor data from seeds.json."""
    seeds_path = Path(__file__).parent.parent / "assets" / "seeds.json"
    with open(seeds_path, 'r') as f:
        return json.load(f)


def create_organizations(session):
    """Create organizations for vendors."""
    print("\n📁 Creating Organizations...")
    
    organizations = [
        {
            "name": "ApolloCRM Inc.",
            "organization_id": "apollo-crm",
            "plan": "enterprise",
            "is_active": True,
        },
        {
            "name": "OrbitCRM Corp.",
            "organization_id": "orbit-crm",
            "plan": "business",
            "is_active": True,
        },
        {
            "name": "CelerityCRM Ltd.",
            "organization_id": "celerity-crm",
            "plan": "business",
            "is_active": True,
        },
        {
            "name": "ZenPayroll Inc.",
            "organization_id": "zen-payroll",
            "plan": "enterprise",
            "is_active": True,
        },
        {
            "name": "SentinelSecure Corp.",
            "organization_id": "sentinel-secure",
            "plan": "enterprise",
            "is_active": True,
        },
        {
            "name": "AtlasAnalytics Inc.",
            "organization_id": "atlas-analytics",
            "plan": "business",
            "is_active": True,
        },
        {
            "name": "GlobalERP Cloud",
            "organization_id": "global-erp",
            "plan": "enterprise",
            "is_active": True,
        },
        {
            "name": "Acme Corp (Buyer)",
            "organization_id": "acme-corp",
            "plan": "enterprise",
            "is_active": True,
        },
    ]
    
    org_map = {}
    for org_data in organizations:
        # Check if organization already exists
        existing = session.query(Organization).filter_by(
            organization_id=org_data["organization_id"]
        ).first()
        if existing:
            print(f"  ✓ Organization already exists: {org_data['name']}")
            org_map[org_data["organization_id"]] = org_data["organization_id"]  # Return string ID
            continue
        
        org = Organization(
            name=org_data["name"],
            organization_id=org_data["organization_id"],
            plan=org_data["plan"],
            is_active=org_data["is_active"],
        )
        session.add(org)
        session.flush()  # Get the ID
        org_map[org_data["organization_id"]] = org_data["organization_id"]  # Return string ID
        print(f"  ✓ Created organization: {org_data['name']} (ID: {org_data['organization_id']})")
    
    session.commit()
    return org_map


def seed_vendors(session, org_map):
    """Seed vendor profiles from seeds.json."""
    vendors_data = load_seed_data()
    
    print(f"\n🏢 Seeding {len(vendors_data)} Vendors...")
    
    for vendor_data in vendors_data:
        # Check if vendor already exists
        existing = session.query(VendorProfileRecord).filter_by(
            vendor_id=vendor_data["id"]
        ).first()
        
        if existing:
            print(f"  ✓ Vendor already exists: {vendor_data['name']}")
            continue
        
        # Map pricing structure
        pricing = vendor_data.get("pricing", {})
        
        vendor = VendorProfileRecord(
            vendor_id=vendor_data["id"],
            name=vendor_data["name"],
            category=vendor_data.get("category"),
            description=f"{vendor_data['name']} - {vendor_data.get('category', 'SaaS')} solution",
            
            # Pricing
            list_price=pricing.get("list_price"),
            price_tiers=pricing.get("tiers"),
            currency="USD",
            
            # Capabilities
            features=vendor_data.get("features", []),
            integrations=vendor_data.get("regions", []),  # Using regions as integrations for now
            
            # Compliance
            certifications=vendor_data.get("compliance", []),
            compliance_frameworks=vendor_data.get("compliance", []),
            
            # Guardrails and policies
            guardrails={
                "min_price": pricing.get("floor"),
                "max_discount": (pricing.get("list_price", 0) - pricing.get("floor", 0)) / pricing.get("list_price", 1) if pricing.get("list_price") else 0,
                "payment_terms": vendor_data.get("payment_terms", []),
                "behavior_profile": vendor_data.get("behavior_profile", "balanced"),
            },
            exchange_policy=vendor_data.get("exchange", {}),
            
            # Metadata
            vendor_metadata={
                "billing_cadence": vendor_data.get("billing_cadence"),
                "support": vendor_data.get("support", {}),
                "regions": vendor_data.get("regions", []),
            },
            
            # Data quality
            confidence_score=1.0,
            data_source="seeds.json",
            last_enriched_at=datetime.utcnow(),
        )
        
        session.add(vendor)
        print(f"  ✓ Created vendor: {vendor_data['name']} ({vendor_data['id']})")
    
    session.commit()
    print(f"\n✅ Successfully seeded {len(vendors_data)} vendors")


def create_test_users(session, org_map):
    """Create test buyer and seller users."""
    print("\n👥 Creating Test Users...")
    
    test_users = [
        # Buyer users
        {
            "username": "buyer_demo",
            "email": "buyer@test.com",
            "password": "test123",
            "full_name": "Demo Buyer",
            "role": "buyer",
            "organization_id": "acme-corp",
            "is_active": True,
        },
        {
            "username": "buyer_admin",
            "email": "admin@acme.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": "buyer",
            "organization_id": "acme-corp",
            "is_active": True,
            "is_superuser": True,
        },
        # Seller users - one for each vendor
        {
            "username": "seller_apollo",
            "email": "seller@apollocrm.com",
            "password": "apollo123",
            "full_name": "Apollo Sales Agent",
            "role": "seller",
            "organization_id": "apollo-crm",
            "is_active": True,
        },
        {
            "username": "seller_orbit",
            "email": "seller@orbitcrm.com",
            "password": "orbit123",
            "full_name": "Orbit Sales Agent",
            "role": "seller",
            "organization_id": "orbit-crm",
            "is_active": True,
        },
        {
            "username": "seller_celerity",
            "email": "seller@celeritycrm.com",
            "password": "celerity123",
            "full_name": "Celerity Sales Agent",
            "role": "seller",
            "organization_id": "celerity-crm",
            "is_active": True,
        },
        {
            "username": "seller_zen",
            "email": "seller@zenpayroll.com",
            "password": "zen123",
            "full_name": "Zen Sales Agent",
            "role": "seller",
            "organization_id": "zen-payroll",
            "is_active": True,
        },
        {
            "username": "seller_sentinel",
            "email": "seller@sentinelsecure.com",
            "password": "sentinel123",
            "full_name": "Sentinel Sales Agent",
            "role": "seller",
            "organization_id": "sentinel-secure",
            "is_active": True,
        },
        {
            "username": "seller_atlas",
            "email": "seller@atlasanalytics.com",
            "password": "atlas123",
            "full_name": "Atlas Sales Agent",
            "role": "seller",
            "organization_id": "atlas-analytics",
            "is_active": True,
        },
        {
            "username": "seller_global",
            "email": "seller@globalerp.com",
            "password": "global123",
            "full_name": "GlobalERP Sales Agent",
            "role": "seller",
            "organization_id": "global-erp",
            "is_active": True,
        },
    ]
    
    for user_data in test_users:
        # Check if user already exists
        existing = session.query(UserAccount).filter_by(
            email=user_data["email"]
        ).first()
        
        if existing:
            print(f"  ✓ User already exists: {user_data['email']}")
            continue
        
        # Get organization ID
        org_id = org_map.get(user_data["organization_id"])
        
        user = UserAccount(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            organization_id=org_id,
            is_active=user_data["is_active"],
            is_superuser=user_data.get("is_superuser", False),
            email_verified=True,  # Auto-verify for test users
            password_changed_at=datetime.utcnow(),
        )
        
        session.add(user)
        print(f"  ✓ Created {user_data['role']} user: {user_data['email']} / {user_data['password']}")
    
    session.commit()
    print(f"\n✅ Successfully created {len(test_users)} test users")


def print_summary():
    """Print summary of seeded data."""
    print("\n" + "="*60)
    print("🎉 SEED DATA SUMMARY")
    print("="*60)
    
    print("\n📊 BUYER TEST ACCOUNTS:")
    print("  • buyer@test.com / test123 (Demo Buyer)")
    print("  • admin@acme.com / admin123 (Admin User - Superuser)")
    
    print("\n🏪 SELLER TEST ACCOUNTS:")
    print("  • seller@apollocrm.com / apollo123 (ApolloCRM)")
    print("  • seller@orbitcrm.com / orbit123 (OrbitCRM)")
    print("  • seller@celeritycrm.com / celerity123 (CelerityCRM)")
    print("  • seller@zenpayroll.com / zen123 (ZenPayroll)")
    print("  • seller@sentinelsecure.com / sentinel123 (SentinelSecure)")
    print("  • seller@atlasanalytics.com / atlas123 (AtlasAnalytics)")
    print("  • seller@globalerp.com / global123 (GlobalERP)")
    
    print("\n🏢 VENDORS SEEDED:")
    print("  • ApolloCRM - Enterprise CRM ($1200/seat/year)")
    print("  • OrbitCRM - Mid-market CRM ($240/seat/year)")
    print("  • CelerityCRM - SMB CRM ($360/seat/year)")
    print("  • ZenPayroll - Payroll ($25/seat/month)")
    print("  • SentinelSecure - Security ($1500/seat/year)")
    print("  • AtlasAnalytics - Analytics ($900/seat/year)")
    print("  • GlobalERP - ERP ($1800/seat/year)")
    
    print("\n🚀 NEXT STEPS:")
    print("  1. Start the API server: python run_api.py")
    print("  2. Login as buyer: buyer@test.com / test123")
    print("  3. Create a procurement request")
    print("  4. Start negotiations with vendors")
    print("  5. Login as seller to view deals: seller@apollocrm.com / apollo123")
    
    print("\n" + "="*60)


def main():
    """Main seeding function."""
    print("\n🌱 Starting Database Seeding Process...")
    print("="*60)
    
    try:
        with session_context() as session:
            # Step 1: Create organizations
            org_map = create_organizations(session)
            
            # Step 2: Seed vendors
            seed_vendors(session, org_map)
            
            # Step 3: Create test users
            create_test_users(session, org_map)
            
            # Print summary
            print_summary()
            
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
