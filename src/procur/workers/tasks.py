"""Celery tasks for async processing."""

import logging
from typing import Any, Dict

from celery import Task

from .celery_app import celery_app
from ..db import get_session
from ..db.repositories import (
    NegotiationRepository,
    VendorRepository,
    ContractRepository,
    RequestRepository,
)
from ..events import EventPublisher, EventType
from ..agents import BuyerAgent, SellerAgent
from ..services import (
    NegotiationEngine,
    PolicyEngine,
    ScoringService,
    ComplianceService,
    GuardrailService,
    AuditTrailService,
    MemoryService,
    ExplainabilityService,
    RetrievalService,
)
from ..llm import LLMClient
from ..integrations import (
    G2Scraper,
    PricingScraper,
    ComplianceScraper,
)
from ..observability import get_logger, track_metric

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        logger.info(f"Task {self.name} succeeded: {task_id}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        logger.error(f"Task {self.name} failed: {task_id} - {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(f"Task {self.name} retrying: {task_id} - {exc}")


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="process_negotiation_round",
    max_retries=3,
    default_retry_delay=60,
)
def process_negotiation_round(
    self,
    negotiation_id: str,
    round_number: int,
    correlation_id: str,
) -> Dict[str, Any]:
    """
    Process a negotiation round.
    
    Args:
        negotiation_id: Negotiation session ID
        round_number: Round number
        correlation_id: Correlation ID for tracking
    
    Returns:
        Result dict
    """
    try:
        logger.info(f"Processing negotiation round: {negotiation_id} - Round {round_number}")
        track_metric("negotiation_round_started", 1, {"negotiation_id": negotiation_id})
        
        with get_session() as session:
            neg_repo = NegotiationRepository(session)
            request_repo = RequestRepository(session)
            vendor_repo = VendorRepository(session)
            
            # Get negotiation session
            negotiation = neg_repo.get_by_session_id(negotiation_id)
            if not negotiation:
                raise ValueError(f"Negotiation not found: {negotiation_id}")
            
            # Get request and vendor
            request = request_repo.get(negotiation.request_id)
            vendor = vendor_repo.get(negotiation.vendor_id)
            
            if not request or not vendor:
                raise ValueError("Request or vendor not found")
            
            # Initialize services
            llm_client = LLMClient()
            policy_engine = PolicyEngine()
            scoring_service = ScoringService()
            compliance_service = ComplianceService()
            guardrail_service = GuardrailService()
            audit_service = AuditTrailService()
            memory_service = MemoryService()
            explainability_service = ExplainabilityService()
            retrieval_service = RetrievalService()
            negotiation_engine = NegotiationEngine(policy_engine, scoring_service)
            
            # Initialize buyer agent
            buyer_agent = BuyerAgent(
                llm_client=llm_client,
                policy_engine=policy_engine,
                scoring_service=scoring_service,
                compliance_service=compliance_service,
                guardrail_service=guardrail_service,
                negotiation_engine=negotiation_engine,
                audit_service=audit_service,
                memory_service=memory_service,
                explainability_service=explainability_service,
                retrieval_service=retrieval_service,
            )
            
            # Initialize seller agent
            seller_agent = SellerAgent(
                llm_client=llm_client,
                negotiation_engine=negotiation_engine,
            )
            
            # Convert DB models to domain models
            from ..models import Request, VendorProfile
            domain_request = Request(
                request_id=request.request_id,
                description=request.description,
                category=request.category or "",
                budget_min=request.budget_min,
                budget_max=request.budget_max,
                quantity=request.quantity or 1,
                must_haves=request.must_haves or [],
                nice_to_haves=request.nice_to_haves or [],
                compliance_requirements=request.compliance_requirements or [],
            )
            
            domain_vendor = VendorProfile(
                vendor_id=vendor.vendor_id,
                name=vendor.name,
                category=vendor.category or "",
                list_price=vendor.list_price or 0.0,
                features=vendor.features or [],
                certifications=vendor.certifications or [],
                compliance_frameworks=vendor.compliance_frameworks or [],
            )
            
            # Execute negotiation round
            # Get history from negotiation session
            history = negotiation.history or []
            
            # Buyer generates offer/counter-offer
            buyer_decision = buyer_agent.negotiate(
                request=domain_request,
                vendor=domain_vendor,
                round_num=round_number,
            )
            
            # Seller responds
            if buyer_decision.offer:
                seller_decision = seller_agent.respond_to_offer(
                    offer=buyer_decision.offer,
                    vendor=domain_vendor,
                    round_num=round_number,
                )
                
                # Update history
                history.append({
                    "round": round_number,
                    "buyer_offer": buyer_decision.offer.model_dump(),
                    "seller_response": seller_decision.model_dump(),
                })
            
            # Update negotiation session
            neg_repo.update(
                negotiation.id,
                current_round=round_number + 1,
                history=history,
                opponent_model=buyer_agent.vendor_states.get(vendor.vendor_id, {}).model_dump() if hasattr(buyer_agent, 'vendor_states') else None,
            )
            
            # Publish round completed event
            publisher = EventPublisher()
            publisher.publish(
                event_type=EventType.NEGOTIATION_ROUND_COMPLETED,
                data={
                    "negotiation_id": negotiation_id,
                    "round_number": round_number,
                    "buyer_decision": buyer_decision.decision,
                },
                correlation_id=correlation_id,
            )
            
            track_metric("negotiation_round_completed", 1, {"negotiation_id": negotiation_id})
            logger.info(f"Completed negotiation round: {negotiation_id} - Round {round_number}")
            
            return {
                "negotiation_id": negotiation_id,
                "round_number": round_number,
                "status": "completed",
                "buyer_decision": buyer_decision.decision,
            }
            
    except Exception as e:
        logger.error(f"Failed to process negotiation round: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="enrich_vendor_data",
    max_retries=3,
    default_retry_delay=300,
)
def enrich_vendor_data(
    self,
    vendor_id: str,
    category: str,
) -> Dict[str, Any]:
    """
    Enrich vendor data from external sources.
    
    Args:
        vendor_id: Vendor ID
        category: Vendor category
    
    Returns:
        Result dict
    """
    try:
        logger.info(f"Enriching vendor data: {vendor_id}")
        track_metric("vendor_enrichment_started", 1, {"vendor_id": vendor_id})
        
        with get_session() as session:
            vendor_repo = VendorRepository(session)
            
            # Get vendor
            vendor = vendor_repo.get_by_vendor_id(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            # Initialize scrapers
            g2_scraper = G2Scraper()
            pricing_scraper = PricingScraper()
            compliance_scraper = ComplianceScraper()
            
            enrichment_data = {}
            
            # Scrape G2 data (ratings, reviews, features)
            try:
                g2_data = g2_scraper.scrape_vendor(vendor.name, category)
                if g2_data:
                    enrichment_data["rating"] = g2_data.get("rating")
                    enrichment_data["review_count"] = g2_data.get("review_count")
                    enrichment_data["features"] = g2_data.get("features", vendor.features)
            except Exception as e:
                logger.warning(f"G2 scraping failed for {vendor_id}: {e}")
            
            # Scrape pricing data
            try:
                pricing_data = pricing_scraper.scrape_pricing(vendor.name, category)
                if pricing_data:
                    enrichment_data["list_price"] = pricing_data.get("list_price")
                    enrichment_data["price_tiers"] = pricing_data.get("price_tiers")
            except Exception as e:
                logger.warning(f"Pricing scraping failed for {vendor_id}: {e}")
            
            # Scrape compliance data
            try:
                compliance_data = compliance_scraper.scrape_compliance(vendor.name)
                if compliance_data:
                    enrichment_data["certifications"] = compliance_data.get("certifications", vendor.certifications)
                    enrichment_data["compliance_frameworks"] = compliance_data.get("frameworks", vendor.compliance_frameworks)
            except Exception as e:
                logger.warning(f"Compliance scraping failed for {vendor_id}: {e}")
            
            # Update vendor with enriched data
            from datetime import datetime, timezone
            enrichment_data["last_enriched_at"] = datetime.now(timezone.utc)
            enrichment_data["confidence_score"] = 0.8  # Calculate based on data completeness
            
            vendor_repo.update(vendor.id, **enrichment_data)
            
            # Publish enrichment completed event
            publisher = EventPublisher()
            publisher.publish(
                event_type=EventType.VENDOR_ENRICHMENT_COMPLETED,
                data={
                    "vendor_id": vendor_id,
                    "category": category,
                    "enriched_fields": list(enrichment_data.keys()),
                },
            )
            
            track_metric("vendor_enrichment_completed", 1, {"vendor_id": vendor_id})
            logger.info(f"Completed vendor enrichment: {vendor_id}")
            
            return {
                "vendor_id": vendor_id,
                "status": "completed",
                "enriched_fields": list(enrichment_data.keys()),
            }
            
    except Exception as e:
        logger.error(f"Failed to enrich vendor data: {e}")
        
        # Publish enrichment failed event
        publisher = EventPublisher()
        publisher.publish(
            event_type=EventType.VENDOR_ENRICHMENT_FAILED,
            data={
                "vendor_id": vendor_id,
                "error": str(e),
            },
        )
        
        raise self.retry(exc=e)


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="generate_contract",
    max_retries=3,
    default_retry_delay=60,
)
def generate_contract(
    self,
    contract_id: str,
    request_id: str,
    vendor_id: str,
    correlation_id: str,
) -> Dict[str, Any]:
    """
    Generate contract document.
    
    Args:
        contract_id: Contract ID
        request_id: Request ID
        vendor_id: Vendor ID
        correlation_id: Correlation ID
    
    Returns:
        Result dict
    """
    try:
        logger.info(f"Generating contract: {contract_id}")
        track_metric("contract_generation_started", 1, {"contract_id": contract_id})
        
        with get_session() as session:
            contract_repo = ContractRepository(session)
            request_repo = RequestRepository(session)
            vendor_repo = VendorRepository(session)
            
            # Get contract
            contract = contract_repo.get_by_contract_id(contract_id)
            if not contract:
                raise ValueError(f"Contract not found: {contract_id}")
            
            # Get related entities
            request = request_repo.get(contract.request_id)
            vendor = vendor_repo.get(contract.vendor_id)
            
            if not request or not vendor:
                raise ValueError("Request or vendor not found")
            
            # Generate contract document using LLM
            llm_client = LLMClient()
            
            contract_prompt = f"""
            Generate a professional procurement contract document with the following details:
            
            VENDOR: {vendor.name}
            BUYER: {request.user_id}
            
            CONTRACT TERMS:
            - Total Value: ${contract.total_value:,.2f} {contract.currency}
            - Start Date: {contract.start_date.strftime('%Y-%m-%d')}
            - End Date: {contract.end_date.strftime('%Y-%m-%d')}
            - Auto-Renew: {"Yes" if contract.auto_renew else "No"}
            - Payment Schedule: {contract.payment_schedule}
            
            REQUIREMENTS:
            - Must-haves: {request.must_haves}
            - Compliance: {request.compliance_requirements}
            
            Generate a complete contract document with standard clauses for:
            1. Scope of Services
            2. Payment Terms
            3. Service Level Agreement (SLA)
            4. Termination Conditions
            5. Data Privacy and Security
            6. Intellectual Property
            7. Limitation of Liability
            8. Dispute Resolution
            """
            
            contract_document = llm_client.generate_completion(
                prompt=contract_prompt,
                max_tokens=4000,
            )
            
            # Store contract document (in production, upload to S3/storage)
            document_url = f"contracts/{contract_id}.pdf"  # Placeholder
            
            # Update contract with generated document
            contract_repo.update(
                contract.id,
                status="generated",
                terms_and_conditions=contract_document,
                document_url=document_url,
            )
            
            # Publish generation completed event
            publisher = EventPublisher()
            publisher.publish(
                event_type=EventType.CONTRACT_GENERATION_COMPLETED,
                data={
                    "contract_id": contract_id,
                    "request_id": request_id,
                    "vendor_id": vendor_id,
                    "document_url": document_url,
                },
                correlation_id=correlation_id,
            )
            
            track_metric("contract_generation_completed", 1, {"contract_id": contract_id})
            logger.info(f"Completed contract generation: {contract_id}")
            
            return {
                "contract_id": contract_id,
                "status": "generated",
                "document_url": document_url,
            }
            
    except Exception as e:
        logger.error(f"Failed to generate contract: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="send_notification",
    max_retries=3,
    default_retry_delay=30,
)
def send_notification(
    self,
    notification_type: str,
    recipient: str,
    subject: str,
    message: str,
    **kwargs,
) -> Dict[str, Any]:
    """
    Send notification.
    
    Args:
        notification_type: Type of notification (email, slack, webhook)
        recipient: Recipient address
        subject: Notification subject
        message: Notification message
        **kwargs: Additional parameters
    
    Returns:
        Result dict
    """
    try:
        logger.info(f"Sending {notification_type} notification to {recipient}")
        track_metric("notification_sent", 1, {"type": notification_type})
        
        from ..integrations import SlackIntegration, SendGridService
        import os
        
        if notification_type == "email":
            # Send email using SendGrid
            api_key = os.getenv("SENDGRID_API_KEY")
            from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@procur.ai")
            
            if not api_key:
                logger.warning("SendGrid API key not configured, skipping email")
                return {
                    "notification_type": notification_type,
                    "recipient": recipient,
                    "status": "skipped",
                    "reason": "no_api_key",
                }
            
            email_service = SendGridService(api_key, from_email)
            email_service.send_email(
                to_email=recipient,
                subject=subject,
                html_content=message,
                **kwargs
            )
        elif notification_type == "slack":
            # Send Slack message
            slack = SlackIntegration()
            slack.send_message(
                channel=recipient,
                text=message,
                **kwargs
            )
        elif notification_type == "webhook":
            # Call webhook
            import requests
            requests.post(
                recipient,
                json={
                    "subject": subject,
                    "message": message,
                    **kwargs
                },
                timeout=10,
            )
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")
        
        logger.info(f"Sent {notification_type} notification to {recipient}")
        
        return {
            "notification_type": notification_type,
            "recipient": recipient,
            "status": "sent",
        }
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise self.retry(exc=e)


@celery_app.task(name="cleanup_old_events")
def cleanup_old_events(days: int = 90):
    """
    Cleanup old events from event store.
    
    Args:
        days: Number of days to keep events
    """
    try:
        logger.info(f"Cleaning up events older than {days} days")
        
        from ..events.store import EventStore
        
        with get_session() as session:
            event_store = EventStore(session)
            count = event_store.cleanup_old_events(days)
            
        logger.info(f"Cleaned up {count} old events")
        
        return {"cleaned_up": count}
        
    except Exception as e:
        logger.error(f"Failed to cleanup old events: {e}")
        raise


# Periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-events-daily": {
        "task": "cleanup_old_events",
        "schedule": 86400.0,  # Daily
        "args": (90,),
    },
}
