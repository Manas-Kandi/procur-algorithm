"""Integration tests for Celery worker tasks."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.procur.db import get_session, init_db
from src.procur.db.repositories import (
    RequestRepository,
    VendorRepository,
    NegotiationRepository,
    ContractRepository,
    UserRepository,
)
from src.procur.workers.tasks import (
    process_negotiation_round,
    enrich_vendor_data,
    generate_contract,
    send_notification,
)


@pytest.fixture(scope="module")
def test_db():
    """Initialize test database."""
    db = init_db(create_tables=True)
    yield db
    db.drop_all_tables()
    db.close()


@pytest.fixture
def test_user(test_db):
    """Create test user."""
    with get_session() as session:
        user_repo = UserRepository(session)
        user = user_repo.create(
            email="worker@procur.com",
            username="workeruser",
            hashed_password="hashed_password_123",
            full_name="Worker User",
            role="buyer",
        )
        return user


@pytest.fixture
def test_vendor(test_db):
    """Create test vendor."""
    with get_session() as session:
        vendor_repo = VendorRepository(session)
        vendor = vendor_repo.create(
            vendor_id="vendor-worker-001",
            name="Worker Test Vendor",
            category="saas",
            list_price=100.0,
            features=["feature1"],
            certifications=["SOC2"],
        )
        return vendor


@pytest.fixture
def test_request(test_db, test_user):
    """Create test request."""
    with get_session() as session:
        request_repo = RequestRepository(session)
        request = request_repo.create(
            request_id="req-worker-001",
            user_id=test_user.id,
            description="Worker test request",
            request_type="saas",
            category="crm",
            status="pending",
            budget_min=5000.0,
            budget_max=10000.0,
            quantity=50,
        )
        return request


@pytest.fixture
def test_negotiation(test_db, test_request, test_vendor):
    """Create test negotiation session."""
    with get_session() as session:
        neg_repo = NegotiationRepository(session)
        negotiation = neg_repo.create(
            session_id="neg-worker-001",
            request_id=test_request.id,
            vendor_id=test_vendor.id,
            status="active",
            current_round=1,
            max_rounds=5,
            started_at=datetime.now(timezone.utc),
        )
        return negotiation


class TestNegotiationRoundTask:
    """Test negotiation round processing task."""
    
    @patch('src.procur.workers.tasks.BuyerAgent')
    @patch('src.procur.workers.tasks.SellerAgent')
    @patch('src.procur.workers.tasks.EventPublisher')
    def test_process_negotiation_round(
        self,
        mock_publisher,
        mock_seller_agent,
        mock_buyer_agent,
        test_negotiation,
    ):
        """Test processing a negotiation round."""
        # Mock agent responses
        mock_buyer_decision = Mock()
        mock_buyer_decision.decision = "counter_offer"
        mock_buyer_decision.offer = Mock()
        mock_buyer_decision.offer.model_dump.return_value = {
            "unit_price": 95.0,
            "quantity": 50,
        }
        
        mock_buyer_agent.return_value.negotiate.return_value = mock_buyer_decision
        
        mock_seller_decision = Mock()
        mock_seller_decision.model_dump.return_value = {
            "decision": "accept",
        }
        
        mock_seller_agent.return_value.respond_to_offer.return_value = mock_seller_decision
        
        # Execute task
        result = process_negotiation_round(
            negotiation_id=test_negotiation.session_id,
            round_number=1,
            correlation_id="test-corr-001",
        )
        
        # Verify result
        assert result["status"] == "completed"
        assert result["negotiation_id"] == test_negotiation.session_id
        assert result["round_number"] == 1
        
        # Verify negotiation was updated
        with get_session() as session:
            neg_repo = NegotiationRepository(session)
            updated_neg = neg_repo.get_by_session_id(test_negotiation.session_id)
            assert updated_neg.current_round == 2  # Incremented
            assert updated_neg.history is not None


class TestVendorEnrichmentTask:
    """Test vendor data enrichment task."""
    
    @patch('src.procur.workers.tasks.G2Scraper')
    @patch('src.procur.workers.tasks.PricingScraper')
    @patch('src.procur.workers.tasks.ComplianceScraper')
    @patch('src.procur.workers.tasks.EventPublisher')
    def test_enrich_vendor_data(
        self,
        mock_publisher,
        mock_compliance_scraper,
        mock_pricing_scraper,
        mock_g2_scraper,
        test_vendor,
    ):
        """Test enriching vendor data."""
        # Mock scraper responses
        mock_g2_scraper.return_value.scrape_vendor.return_value = {
            "rating": 4.5,
            "review_count": 1000,
            "features": ["email", "mobile", "analytics"],
        }
        
        mock_pricing_scraper.return_value.scrape_pricing.return_value = {
            "list_price": 120.0,
            "price_tiers": {"1-10": 150, "11-50": 120, "51+": 100},
        }
        
        mock_compliance_scraper.return_value.scrape_compliance.return_value = {
            "certifications": ["SOC2", "ISO27001", "GDPR"],
            "frameworks": ["NIST", "CIS"],
        }
        
        # Execute task
        result = enrich_vendor_data(
            vendor_id=test_vendor.vendor_id,
            category="saas",
        )
        
        # Verify result
        assert result["status"] == "completed"
        assert result["vendor_id"] == test_vendor.vendor_id
        assert "enriched_fields" in result
        
        # Verify vendor was updated
        with get_session() as session:
            vendor_repo = VendorRepository(session)
            updated_vendor = vendor_repo.get_by_vendor_id(test_vendor.vendor_id)
            assert updated_vendor.rating == 4.5
            assert updated_vendor.review_count == 1000
            assert updated_vendor.last_enriched_at is not None


class TestContractGenerationTask:
    """Test contract generation task."""
    
    @patch('src.procur.workers.tasks.LLMClient')
    @patch('src.procur.workers.tasks.EventPublisher')
    def test_generate_contract(
        self,
        mock_publisher,
        mock_llm_client,
        test_db,
        test_request,
        test_vendor,
    ):
        """Test generating a contract document."""
        # Create contract
        with get_session() as session:
            contract_repo = ContractRepository(session)
            contract = contract_repo.create(
                contract_id="contract-001",
                request_id=test_request.id,
                vendor_id=test_vendor.id,
                total_value=5000.0,
                currency="USD",
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc),
                auto_renew=False,
                status="pending",
            )
        
        # Mock LLM response
        mock_llm_client.return_value.generate_completion.return_value = (
            "CONTRACT AGREEMENT\n\nThis agreement is made between..."
        )
        
        # Execute task
        result = generate_contract(
            contract_id=contract.contract_id,
            request_id=test_request.request_id,
            vendor_id=test_vendor.vendor_id,
            correlation_id="test-corr-002",
        )
        
        # Verify result
        assert result["status"] == "generated"
        assert result["contract_id"] == contract.contract_id
        assert "document_url" in result
        
        # Verify contract was updated
        with get_session() as session:
            contract_repo = ContractRepository(session)
            updated_contract = contract_repo.get_by_contract_id(contract.contract_id)
            assert updated_contract.status == "generated"
            assert updated_contract.terms_and_conditions is not None


class TestNotificationTask:
    """Test notification sending task."""
    
    @patch('src.procur.workers.tasks.EmailService')
    def test_send_email_notification(self, mock_email_service):
        """Test sending email notification."""
        result = send_notification(
            notification_type="email",
            recipient="test@example.com",
            subject="Test Subject",
            message="Test message",
        )
        
        assert result["status"] == "sent"
        assert result["notification_type"] == "email"
        mock_email_service.return_value.send_email.assert_called_once()
    
    @patch('src.procur.workers.tasks.SlackIntegration')
    def test_send_slack_notification(self, mock_slack):
        """Test sending Slack notification."""
        result = send_notification(
            notification_type="slack",
            recipient="#general",
            subject="Test Subject",
            message="Test message",
        )
        
        assert result["status"] == "sent"
        assert result["notification_type"] == "slack"
        mock_slack.return_value.send_message.assert_called_once()
    
    @patch('requests.post')
    def test_send_webhook_notification(self, mock_post):
        """Test sending webhook notification."""
        mock_post.return_value.status_code = 200
        
        result = send_notification(
            notification_type="webhook",
            recipient="https://example.com/webhook",
            subject="Test Subject",
            message="Test message",
        )
        
        assert result["status"] == "sent"
        assert result["notification_type"] == "webhook"
        mock_post.assert_called_once()
