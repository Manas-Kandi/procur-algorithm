#!/usr/bin/env python3
"""
Seed demo data for frontend-backend integration testing.

This script:
1. Seeds vendors from assets/seeds.json into the database
2. Creates test buyer and seller users
3. Creates sample requests and contracts for portfolio testing
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from procur.db.session import get_session
from procur.db.repositories import (
    VendorRepository,
    UserRepository,
    RequestRepository,
    ContractRepository,
)
from procur.api.security import get_password_hash
from passlib.context import CryptContext


def get_password_context():
    """Get password hashing context"""
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_vendors():
    """Seed vendors from seeds.json"""
    seeds_path = Path(__file__).parent.parent / "assets" / "seeds.json"

    with open(seeds_path) as f:
        vendors_data = json.load(f)

    session = next(get_session())
    vendor_repo = VendorRepository(session)

    seeded_count = 0
    for vendor_data in vendors_data:
        # Check if vendor already exists
        existing = vendor_repo.get_by_vendor_id(vendor_data['id'])
        if existing:
            print(f"✓ Vendor {vendor_data['name']} already exists, skipping")
            continue

        # Map seeds.json format to VendorProfileRecord fields
        vendor_repo.create(
            vendor_id=vendor_data['id'],
            name=vendor_data['name'],
            category=vendor_data['category'],
            list_price=vendor_data['pricing']['list_price'],
            price_tiers=vendor_data['pricing'].get('tiers', {}),
            currency='USD',
            features=vendor_data.get('features', []),
            certifications=vendor_data.get('compliance', []),
            compliance_frameworks=vendor_data.get('compliance', []),
            guardrails={
                'price_floor': vendor_data['pricing']['floor'],
                'behavior_profile': vendor_data.get('behavior_profile', 'balanced'),
            },
            exchange_policy=vendor_data.get('exchange', {}),
            rating=4.5,  # Default rating
            confidence_score=0.95,
            data_source='seeds.json',
        )
        seeded_count += 1
        print(f"✓ Seeded vendor: {vendor_data['name']}")

    session.commit()
    print(f"\n✅ Seeded {seeded_count} vendors (skipped {len(vendors_data) - seeded_count} existing)")
    return vendors_data


async def create_test_users():
    """Create test buyer and seller users"""
    session = next(get_session())
    user_repo = UserRepository(session)
    pwd_context = get_password_context()

    # Create test buyer
    buyer_email = 'buyer@test.com'
    buyer_password = 'password123'  # 8+ characters required
    buyer = user_repo.get_by_email(buyer_email)
    if not buyer:
        user_repo.create(
            username='buyer_demo',
            email=buyer_email,
            hashed_password=pwd_context.hash(buyer_password),
            role='buyer',
            organization_id='test-org',
            is_active=True,
        )
        print(f"✓ Created buyer: {buyer_email} / {buyer_password}")
    else:
        print(f"✓ Buyer {buyer_email} already exists")

    # Create test seller (linked to ApolloCRM)
    seller_email = 'seller@apollocrm.com'
    seller_password = 'password123'  # 8+ characters required
    seller = user_repo.get_by_email(seller_email)
    if not seller:
        user_repo.create(
            username='seller_apollo',
            email=seller_email,
            hashed_password=pwd_context.hash(seller_password),
            role='seller',
            organization_id='apollo-crm',  # Link to vendor
            is_active=True,
        )
        print(f"✓ Created seller: {seller_email} / {seller_password}")
    else:
        print(f"✓ Seller {seller_email} already exists")

    session.commit()
    print("\n✅ Test users created")


async def create_sample_portfolio_data():
    """Create sample requests and contracts for portfolio testing"""
    session = next(get_session())
    user_repo = UserRepository(session)
    request_repo = RequestRepository(session)
    contract_repo = ContractRepository(session)
    vendor_repo = VendorRepository(session)

    # Get buyer user
    buyer = user_repo.get_by_email('buyer@test.com')
    if not buyer:
        print("⚠️  Buyer user not found, skipping portfolio data")
        return

    # Get some vendors
    vendors = vendor_repo.get_all_active()
    if len(vendors) < 3:
        print("⚠️  Not enough vendors, skipping portfolio data")
        return

    # Create 3 sample requests with contracts (for portfolio)
    portfolio_items = [
        {
            'vendor': vendors[0],  # ApolloCRM
            'description': 'CRM for sales team',
            'quantity': 50,
            'budget_max': 60000,
            'seats_active': 42,  # 84% utilization
            'months_ago': 8,
        },
        {
            'vendor': vendors[3],  # ZenPayroll
            'description': 'Payroll processing service',
            'quantity': 100,
            'budget_max': 2500,
            'seats_active': 100,  # 100% utilization
            'months_ago': 3,
        },
        {
            'vendor': vendors[4],  # SentinelSecure
            'description': 'Security monitoring platform',
            'quantity': 25,
            'budget_max': 37500,
            'seats_active': 15,  # 60% utilization - underutilized
            'months_ago': 10,
        },
    ]

    for idx, item in enumerate(portfolio_items):
        # Create request
        request = request_repo.create(
            request_id=f"req-portfolio-{idx}",
            user_id=buyer.id,
            description=item['description'],
            type='saas',
            category=item['vendor'].category,
            quantity=item['quantity'],
            budget_max=item['budget_max'],
            currency='USD',
            status='contracted',
            must_haves=['api', 'sso'],
            compliance_requirements=['SOC2'],
        )

        # Create contract
        start_date = datetime.utcnow() - timedelta(days=30 * item['months_ago'])
        renewal_date = start_date + timedelta(days=365)

        contract = contract_repo.create(
            contract_id=f"contract-portfolio-{idx}",
            request_id=request.id,
            vendor_id=item['vendor'].id,
            unit_price=item['budget_max'] / item['quantity'],
            quantity=item['quantity'],
            term_months=12,
            payment_terms='NET30',
            total_value=item['budget_max'],
            currency='USD',
            start_date=start_date.date(),
            end_date=(start_date + timedelta(days=365)).date(),
            renewal_date=renewal_date.date(),
            auto_renew=True,
            status='active',
            signed_by_buyer=True,
            signed_by_vendor=True,
            buyer_signature_date=start_date.date(),
            vendor_signature_date=start_date.date(),
        )

        print(f"✓ Created portfolio item: {item['vendor'].name} ({item['seats_active']}/{item['quantity']} seats)")

    session.commit()
    print("\n✅ Sample portfolio data created")


async def main():
    print("🚀 Seeding demo data for Procur...\n")

    # Step 1: Seed vendors
    print("=" * 60)
    print("STEP 1: Seeding vendors from seeds.json")
    print("=" * 60)
    vendors = await seed_vendors()

    # Step 2: Create test users
    print("\n" + "=" * 60)
    print("STEP 2: Creating test users")
    print("=" * 60)
    await create_test_users()

    # Step 3: Create sample portfolio data
    print("\n" + "=" * 60)
    print("STEP 3: Creating sample portfolio data")
    print("=" * 60)
    await create_sample_portfolio_data()

    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    print("\nTest Credentials:")
    print("  Buyer:  buyer@test.com / password123")
    print("  Seller: seller@apollocrm.com / password123")
    print(f"\nSeeded {len(vendors)} vendors and 3 portfolio contracts")
    print("\nNext steps:")
    print("  1. Start the backend: python run_api.py")
    print("  2. Start the frontend: cd frontend && npm run dev")
    print("  3. Login as buyer@test.com to test the flow")


if __name__ == '__main__':
    asyncio.run(main())
