#!/usr/bin/env python
"""Test vendor lookup to debug negotiation enrichment."""

from src.procur.db import SessionLocal
from src.procur.db.repositories import VendorRepository, NegotiationRepository

db = SessionLocal()

try:
    vendor_repo = VendorRepository(db)
    neg_repo = NegotiationRepository(db)
    
    # Get a negotiation
    negs = neg_repo.get_all(limit=1)
    if negs:
        neg = negs[0]
        print(f"Negotiation ID: {neg.id}")
        print(f"Vendor ID: {neg.vendor_id}")
        print(f"Vendor ID type: {type(neg.vendor_id)}")
        
        # Try to get vendor
        vendor = vendor_repo.get_by_id(neg.vendor_id)
        print(f"Vendor found: {vendor}")
        if vendor:
            print(f"Vendor name: {vendor.name}")
        else:
            print("Vendor is None!")
            
            # Try to get all vendors
            all_vendors = vendor_repo.get_all()
            print(f"Total vendors in DB: {len(all_vendors)}")
            if all_vendors:
                print(f"First vendor: ID={all_vendors[0].id}, name={all_vendors[0].name}")
    else:
        print("No negotiations found")
        
finally:
    db.close()
