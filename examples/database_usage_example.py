#!/usr/bin/env python
"""
Example demonstrating database persistence layer usage.

This example shows how to:
1. Initialize the database
2. Create users, requests, vendors, and offers
3. Track negotiation sessions
4. Log audit events
5. Query and update data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.db import init_db, get_session
from procur.db.repositories import (
    UserRepository,
    RequestRepository,
    VendorRepository,
    OfferRepository,
    NegotiationRepository,
    ContractRepository,
    AuditRepository,
)


def main():
    """Run database usage example."""
    print("=" * 80)
    print("Procur Database Persistence Layer - Usage Example")
    print("=" * 80)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        db = init_db(create_tables=True)
        print(f"   ✅ Connected to: {db.config.host}:{db.config.port}/{db.config.database}")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        print("\n   Please ensure PostgreSQL is running and configured correctly.")
        print("   Run: ./scripts/setup_postgres.sh")
        return
    
    # Create sample data
    with get_session() as session:
        user_repo = UserRepository(session)
        request_repo = RequestRepository(session)
        vendor_repo = VendorRepository(session)
        offer_repo = OfferRepository(session)
        neg_repo = NegotiationRepository(session)
        contract_repo = ContractRepository(session)
        audit_repo = AuditRepository(session)
        
        # 2. Create a user
        print("\n2. Creating user account...")
        user = user_repo.create(
            email="john.buyer@acme.com",
            username="john_buyer",
            hashed_password="$2b$12$hashed_password_here",  # In production, use proper hashing
            full_name="John Buyer",
            role="buyer",
            organization_id="acme-corp",
            team="procurement",
        )
        print(f"   ✅ Created user: {user.email} (ID: {user.id})")
        
        # Log user creation
        audit_repo.log_action(
            action="create_user",
            resource_type="user",
            resource_id=str(user.id),
            actor_type="system",
            event_data={"email": user.email, "role": user.role},
        )
        
        # 3. Create a procurement request
        print("\n3. Creating procurement request...")
        request = request_repo.create(
            request_id="req-2025-001",
            user_id=user.id,
            description="Need CRM software for 50 sales representatives",
            request_type="saas",
            category="crm",
            budget_min=50000.0,
            budget_max=75000.0,
            quantity=50,
            billing_cadence="per_seat_per_year",
            must_haves=["api_access", "mobile_app", "reporting"],
            nice_to_haves=["ai_insights", "custom_workflows"],
            compliance_requirements=["SOC2", "GDPR"],
            specs={"deployment": "cloud", "support_level": "premium"},
            status="pending",
        )
        print(f"   ✅ Created request: {request.request_id} (ID: {request.id})")
        
        # Log request creation
        audit_repo.log_action(
            action="create_request",
            resource_type="request",
            resource_id=request.request_id,
            actor_type="user",
            user_id=user.id,
            event_data={
                "category": request.category,
                "budget_max": request.budget_max,
                "quantity": request.quantity,
            },
        )
        
        # 4. Create vendor profiles
        print("\n4. Creating vendor profiles...")
        vendors = []
        
        vendor1 = vendor_repo.create(
            vendor_id="salesforce",
            name="Salesforce",
            website="https://www.salesforce.com",
            description="Leading CRM platform",
            category="crm",
            list_price=150.0,
            price_tiers={"1-10": 150, "11-50": 140, "51-100": 130},
            features=["api_access", "mobile_app", "reporting", "ai_insights"],
            certifications=["SOC2_TYPE2", "ISO27001"],
            compliance_frameworks=["GDPR", "CCPA"],
            guardrails={"price_floor": 120.0, "min_term_months": 12},
            rating=4.5,
            review_count=15000,
            confidence_score=0.95,
            data_source="g2_scraper",
        )
        vendors.append(vendor1)
        print(f"   ✅ Created vendor: {vendor1.name} (ID: {vendor1.id})")
        
        vendor2 = vendor_repo.create(
            vendor_id="hubspot",
            name="HubSpot CRM",
            website="https://www.hubspot.com",
            description="All-in-one CRM platform",
            category="crm",
            list_price=120.0,
            price_tiers={"1-10": 120, "11-50": 110, "51-100": 100},
            features=["api_access", "mobile_app", "reporting", "marketing_automation"],
            certifications=["SOC2_TYPE2"],
            compliance_frameworks=["GDPR"],
            guardrails={"price_floor": 95.0, "min_term_months": 12},
            rating=4.3,
            review_count=12000,
            confidence_score=0.92,
            data_source="g2_scraper",
        )
        vendors.append(vendor2)
        print(f"   ✅ Created vendor: {vendor2.name} (ID: {vendor2.id})")
        
        # 5. Create negotiation sessions
        print("\n5. Starting negotiation sessions...")
        
        for vendor in vendors:
            # Create negotiation session
            neg_session = neg_repo.create(
                session_id=f"neg-{request.request_id}-{vendor.vendor_id}",
                request_id=request.id,
                vendor_id=vendor.id,
                status="active",
                current_round=1,
                max_rounds=8,
                buyer_state={"target_price": 1200.0, "strategy": "price_anchor"},
                seller_state={"list_price": vendor.list_price, "floor_price": vendor.guardrails.get("price_floor")},
            )
            print(f"   ✅ Started negotiation: {neg_session.session_id}")
            
            # Create initial offer from seller
            offer = offer_repo.create(
                offer_id=f"offer-{neg_session.session_id}-r1",
                request_id=request.id,
                vendor_id=vendor.id,
                negotiation_session_id=neg_session.id,
                unit_price=vendor.list_price,
                quantity=request.quantity,
                term_months=12,
                payment_terms="NET30",
                currency="USD",
                round_number=1,
                actor="seller",
                strategy="anchor_high",
                rationale=["Initial offer at list price", "12-month term standard"],
                utility_seller=0.85,
                tco=vendor.list_price * request.quantity * 12,
            )
            print(f"      • Initial offer: ${offer.unit_price}/seat/year")
            
            # Log negotiation start
            audit_repo.log_action(
                action="start_negotiation",
                resource_type="negotiation_session",
                resource_id=neg_session.session_id,
                actor_type="system",
                negotiation_session_id=neg_session.id,
                event_data={
                    "vendor": vendor.name,
                    "initial_price": offer.unit_price,
                },
            )
        
        # 6. Simulate negotiation progress
        print("\n6. Simulating negotiation rounds...")
        
        # Get first negotiation session
        neg_session = neg_repo.get_by_request(request.id)[0]
        vendor = vendor_repo.get_by_id(neg_session.vendor_id)
        
        # Buyer counter-offer
        neg_repo.increment_round(neg_session.id)
        
        buyer_offer = offer_repo.create(
            offer_id=f"offer-{neg_session.session_id}-r2-buyer",
            request_id=request.id,
            vendor_id=vendor.id,
            negotiation_session_id=neg_session.id,
            unit_price=125.0,
            quantity=request.quantity,
            term_months=24,
            payment_terms="NET15",
            currency="USD",
            round_number=2,
            actor="buyer",
            strategy="term_trade",
            rationale=[
                "Offering longer 24-month term for better pricing",
                "Faster payment terms (NET15) for additional discount",
            ],
            utility_buyer=0.75,
            tco=125.0 * request.quantity * 24,
        )
        print(f"   • Round 2 - Buyer counter: ${buyer_offer.unit_price}/seat/year (24mo term)")
        
        # Seller counter-offer
        neg_repo.increment_round(neg_session.id)
        
        seller_counter = offer_repo.create(
            offer_id=f"offer-{neg_session.session_id}-r3-seller",
            request_id=request.id,
            vendor_id=vendor.id,
            negotiation_session_id=neg_session.id,
            unit_price=135.0,
            quantity=request.quantity,
            term_months=24,
            payment_terms="NET15",
            currency="USD",
            discount_percent=10.0,
            value_adds=["Premium support", "Onboarding training"],
            round_number=3,
            actor="seller",
            strategy="term_value",
            rationale=[
                "Accepting 24-month term with 10% discount",
                "Adding premium support and training as value-adds",
            ],
            utility_seller=0.72,
            tco=135.0 * request.quantity * 24,
        )
        print(f"   • Round 3 - Seller counter: ${seller_counter.unit_price}/seat/year + value-adds")
        
        # Accept offer
        offer_repo.accept_offer(seller_counter.id)
        print(f"   ✅ Offer accepted!")
        
        # Complete negotiation
        savings = (vendor.list_price - seller_counter.unit_price) * request.quantity * 24
        neg_repo.complete_session(
            neg_session.id,
            outcome="accepted",
            outcome_reason="Reached mutually beneficial agreement",
            final_offer_id=seller_counter.id,
            savings_achieved=savings,
        )
        
        # 7. Create contract
        print("\n7. Creating contract...")
        contract = contract_repo.create(
            contract_id=f"contract-{request.request_id}-{vendor.vendor_id}",
            request_id=request.id,
            vendor_id=vendor.id,
            final_offer_id=seller_counter.id,
            unit_price=seller_counter.unit_price,
            quantity=seller_counter.quantity,
            term_months=seller_counter.term_months,
            payment_terms=seller_counter.payment_terms,
            total_value=seller_counter.unit_price * seller_counter.quantity * seller_counter.term_months,
            currency="USD",
            value_adds=seller_counter.value_adds,
            status="draft",
        )
        print(f"   ✅ Created contract: {contract.contract_id}")
        print(f"      • Total value: ${contract.total_value:,.2f}")
        print(f"      • Savings: ${savings:,.2f}")
        
        # Log contract creation
        audit_repo.log_action(
            action="create_contract",
            resource_type="contract",
            resource_id=contract.contract_id,
            actor_type="user",
            user_id=user.id,
            event_data={
                "vendor": vendor.name,
                "total_value": contract.total_value,
                "savings": savings,
            },
        )
        
        # 8. Query and display results
        print("\n8. Querying data...")
        
        # Get all requests for user
        user_requests = request_repo.get_by_user(user.id)
        print(f"   • User has {len(user_requests)} request(s)")
        
        # Get all vendors in category
        crm_vendors = vendor_repo.get_by_category("crm")
        print(f"   • Found {len(crm_vendors)} CRM vendor(s)")
        
        # Get all offers for request
        all_offers = offer_repo.get_by_request(request.id)
        print(f"   • Request has {len(all_offers)} offer(s)")
        
        # Get accepted offers
        accepted_offers = offer_repo.get_accepted_offers(request.id)
        print(f"   • {len(accepted_offers)} offer(s) accepted")
        
        # Get audit logs for user
        user_audit_logs = audit_repo.get_by_user(user.id)
        print(f"   • {len(user_audit_logs)} audit log(s) for user")
        
        # Get contracts by status
        draft_contracts = contract_repo.get_by_status("draft")
        print(f"   • {len(draft_contracts)} draft contract(s)")
        
        print("\n" + "=" * 80)
        print("✅ Example completed successfully!")
        print("=" * 80)
        print("\nSummary:")
        print(f"  • Created 1 user account")
        print(f"  • Created 1 procurement request")
        print(f"  • Created 2 vendor profiles")
        print(f"  • Ran 2 negotiation sessions")
        print(f"  • Generated {len(all_offers)} offers")
        print(f"  • Created 1 contract")
        print(f"  • Logged {len(user_audit_logs)} audit events")
        print(f"  • Total savings: ${savings:,.2f}")
        print("\nAll data persisted to PostgreSQL database!")


if __name__ == "__main__":
    main()
