"""Integration tests for API endpoints with database."""

import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from src.procur.api.app import app
from src.procur.db import get_session, init_db
from src.procur.db.repositories import (
    UserRepository,
    RequestRepository,
    VendorRepository,
    NegotiationRepository,
)
from src.procur.api.security import create_access_token


@pytest.fixture(scope="module")
def test_db():
    """Initialize test database."""
    db = init_db(create_tables=True)
    yield db
    db.drop_all_tables()
    db.close()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(test_db):
    """Create test user."""
    with get_session() as session:
        user_repo = UserRepository(session)
        user = user_repo.create(
            email="test@procur.com",
            username="testuser",
            hashed_password="hashed_password_123",
            full_name="Test User",
            role="buyer",
        )
        session.commit()
        return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    # Use user_id as sub claim (get_current_user expects integer user_id)
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_vendor(test_db):
    """Create test vendor."""
    with get_session() as session:
        vendor_repo = VendorRepository(session)
        vendor = vendor_repo.create(
            vendor_id="vendor-001",
            name="Test Vendor",
            category="saas",
            list_price=100.0,
            features=["feature1", "feature2"],
            certifications=["SOC2", "ISO27001"],
        )
        return vendor


class TestRequestAPI:
    """Test request API endpoints."""
    
    def test_create_request(self, client, test_user, auth_headers):
        """Test creating a procurement request."""
        response = client.post(
            "/requests",
            json={
                "description": "Need CRM software",
                "request_type": "saas",
                "category": "crm",
                "budget_min": 5000,
                "budget_max": 10000,
                "quantity": 50,
                "billing_cadence": "monthly",
                "must_haves": ["email integration", "mobile app"],
                "nice_to_haves": ["ai features"],
                "compliance_requirements": [],
                "specs": {},
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Need CRM software"
        assert data["category"] == "crm"
        assert "request_id" in data
    
    def test_get_request(self, client, test_user, auth_headers):
        """Test retrieving a request."""
        # Create request first
        with get_session() as session:
            request_repo = RequestRepository(session)
            request = request_repo.create(
                request_id="req-001",
                user_id=test_user.id,
                description="Test request",
                request_type="saas",
                category="crm",
                status="pending",
            )
            session.commit()
        
        response = client.get(f"/requests/{request.request_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "req-001"
        assert data["description"] == "Test request"
    
    def test_list_requests(self, client, test_user, auth_headers):
        """Test listing requests."""
        response = client.get(
            "/requests",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestVendorAPI:
    """Test vendor API endpoints."""
    
    def test_create_vendor(self, client, auth_headers):
        """Test creating a vendor profile."""
        response = client.post(
            "/vendors",
            json={
                "name": "Salesforce",
                "category": "crm",
                "list_price": 150.0,
                "features": ["email", "mobile", "analytics"],
                "certifications": ["SOC2", "ISO27001"],
                "compliance_frameworks": [],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Salesforce"
        assert "vendor_id" in data
    
    def test_get_vendor(self, client, test_vendor, auth_headers):
        """Test retrieving a vendor."""
        response = client.get(f"/vendors/{test_vendor.vendor_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["vendor_id"] == test_vendor.vendor_id
        assert data["name"] == test_vendor.name
    
    def test_search_vendors(self, client, auth_headers):
        """Test searching vendors by category."""
        response = client.get("/vendors/search?category=saas", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestNegotiationAPI:
    """Test negotiation API endpoints."""
    
    def test_start_negotiation(self, client, test_user, test_vendor, auth_headers):
        """Test starting a negotiation session."""
        # Create request first
        with get_session() as session:
            request_repo = RequestRepository(session)
            request = request_repo.create(
                request_id="req-002",
                user_id=test_user.id,
                description="Test negotiation",
                request_type="saas",
                category="crm",
                status="pending",
            )
            session.commit()
        
        response = client.post(
            "/negotiations",
            json={
                "request_id": request.request_id,
                "vendor_id": test_vendor.vendor_id,
                "max_rounds": 5,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert "session_id" in data
    
    def test_get_negotiation(self, client, test_user, test_vendor, auth_headers):
        """Test retrieving negotiation session."""
        # Create negotiation first
        with get_session() as session:
            request_repo = RequestRepository(session)
            neg_repo = NegotiationRepository(session)
            
            request = request_repo.create(
                request_id="req-003",
                user_id=test_user.id,
                description="Test",
                request_type="saas",
                status="pending",
            )
            
            negotiation = neg_repo.create(
                session_id="neg-001",
                request_id=request.id,
                vendor_id=test_vendor.id,
                status="active",
                current_round=1,
                max_rounds=5,
            )
            session.commit()
        
        response = client.get(f"/negotiations/{negotiation.session_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "neg-001"
        assert data["status"] == "active"


class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_readiness_check(self, client, test_db):
        """Test readiness check endpoint."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
