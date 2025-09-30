#!/usr/bin/env python
"""
Example demonstrating Procur REST API usage.

This example shows how to:
1. Register a user
2. Login and get JWT token
3. Create a procurement request
4. List vendors
5. Get negotiation status
6. Approve an offer
7. Sign a contract
"""

import requests
from typing import Optional


class ProcurAPIClient:
    """Simple client for Procur API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client."""
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def _headers(self) -> dict:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, email: str, username: str, password: str, full_name: str = None):
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name,
            },
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str):
        """Login and get access token."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def get_me(self):
        """Get current user info."""
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def create_request(self, description: str, category: str, budget_max: float, quantity: int, **kwargs):
        """Create a procurement request."""
        data = {
            "description": description,
            "category": category,
            "budget_max": budget_max,
            "quantity": quantity,
            **kwargs,
        }
        response = requests.post(
            f"{self.base_url}/requests",
            json=data,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def list_requests(self, status: str = None):
        """List procurement requests."""
        params = {}
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/requests",
            params=params,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_request(self, request_id: str):
        """Get a specific request."""
        response = requests.get(
            f"{self.base_url}/requests/{request_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def list_vendors(self, category: str = None, search: str = None):
        """List vendors."""
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        
        response = requests.get(
            f"{self.base_url}/vendors",
            params=params,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_vendor(self, vendor_id: str):
        """Get a specific vendor."""
        response = requests.get(
            f"{self.base_url}/vendors/{vendor_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_negotiation(self, session_id: str):
        """Get negotiation session."""
        response = requests.get(
            f"{self.base_url}/negotiations/{session_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_negotiation_offers(self, session_id: str):
        """Get offers in a negotiation."""
        response = requests.get(
            f"{self.base_url}/negotiations/{session_id}/offers",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def approve_negotiation(self, session_id: str, offer_id: int, notes: str = None):
        """Approve a negotiation offer."""
        response = requests.post(
            f"{self.base_url}/negotiations/{session_id}/approve",
            json={"offer_id": offer_id, "notes": notes},
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def list_contracts(self, status: str = None):
        """List contracts."""
        params = {}
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/contracts",
            params=params,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_contract(self, contract_id: str):
        """Get a specific contract."""
        response = requests.get(
            f"{self.base_url}/contracts/{contract_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def sign_contract(self, contract_id: str, signature_type: str = "buyer"):
        """Sign a contract."""
        response = requests.post(
            f"{self.base_url}/contracts/{contract_id}/sign",
            json={"signature_type": signature_type},
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def main():
    """Run API usage example."""
    print("=" * 80)
    print("Procur REST API - Usage Example")
    print("=" * 80)
    
    # Initialize client
    client = ProcurAPIClient("http://localhost:8000")
    
    # 1. Health check
    print("\n1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   ✅ API Status: {health['status']}")
        print(f"   Database: {health['database']}")
    except Exception as e:
        print(f"   ❌ API not available: {e}")
        print("\n   Please start the API server first:")
        print("   python run_api.py")
        return
    
    # 2. Register user
    print("\n2. Registering new user...")
    try:
        user = client.register(
            email="demo@procur.ai",
            username="demo_user",
            password="SecurePassword123!",
            full_name="Demo User",
        )
        print(f"   ✅ User registered: {user['email']}")
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            print("   ℹ️  User already exists, continuing...")
        else:
            raise
    
    # 3. Login
    print("\n3. Logging in...")
    token_data = client.login("demo_user", "SecurePassword123!")
    print(f"   ✅ Logged in successfully")
    print(f"   Token: {token_data['access_token'][:50]}...")
    
    # 4. Get current user
    print("\n4. Getting current user info...")
    me = client.get_me()
    print(f"   ✅ User: {me['username']} ({me['email']})")
    print(f"   Role: {me['role']}")
    
    # 5. Create procurement request
    print("\n5. Creating procurement request...")
    request = client.create_request(
        description="Need CRM software for 50 sales representatives with mobile app and API access",
        category="crm",
        budget_max=75000.0,
        quantity=50,
        must_haves=["api_access", "mobile_app", "reporting"],
        compliance_requirements=["SOC2", "GDPR"],
    )
    print(f"   ✅ Request created: {request['request_id']}")
    print(f"   Budget: ${request['budget_max']:,.2f}")
    print(f"   Quantity: {request['quantity']} seats")
    
    # 6. List requests
    print("\n6. Listing procurement requests...")
    requests_list = client.list_requests(status="pending")
    print(f"   ✅ Found {len(requests_list)} pending request(s)")
    
    # 7. List vendors
    print("\n7. Searching for CRM vendors...")
    vendors = client.list_vendors(category="crm")
    print(f"   ✅ Found {len(vendors)} CRM vendor(s)")
    for vendor in vendors[:3]:
        print(f"      • {vendor['name']} - ${vendor.get('list_price', 'N/A')}/seat")
    
    # 8. Get specific vendor
    if vendors:
        print("\n8. Getting vendor details...")
        vendor = client.get_vendor(vendors[0]['vendor_id'])
        print(f"   ✅ Vendor: {vendor['name']}")
        print(f"   Category: {vendor['category']}")
        print(f"   Features: {len(vendor.get('features', []))} features")
        print(f"   Certifications: {', '.join(vendor.get('certifications', []))}")
    
    print("\n" + "=" * 80)
    print("✅ API Example Completed Successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run negotiations using the BuyerAgent")
    print("2. Use GET /negotiations/{id} to check status")
    print("3. Use POST /negotiations/{id}/approve to approve offers")
    print("4. Use POST /contracts/{id}/sign to sign contracts")
    print("\nAPI Documentation:")
    print("- Swagger UI: http://localhost:8000/docs")
    print("- ReDoc: http://localhost:8000/redoc")


if __name__ == "__main__":
    main()
