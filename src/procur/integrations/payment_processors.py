"""Payment processor integrations (Stripe, PayPal)."""

import logging
from typing import Any, Dict, Optional

import stripe

logger = logging.getLogger(__name__)


class StripeIntegration:
    """Stripe payment processor integration."""
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        """
        Initialize Stripe integration.
        
        Args:
            api_key: Stripe API key
            webhook_secret: Webhook signing secret
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret
    
    def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
        customer_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create payment intent.
        
        Args:
            amount: Amount in cents
            currency: Currency code
            metadata: Additional metadata
            customer_email: Customer email
        
        Returns:
            Payment intent dict
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                receipt_email=customer_email,
            )
            
            logger.info(f"Created Stripe payment intent: {intent.id}")
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise
    
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create Stripe customer.
        
        Returns:
            Customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create subscription."""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
            )
            
            logger.info(f"Created subscription: {subscription.id}")
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    def verify_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify and parse webhook event.
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
        
        Returns:
            Event dict
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            logger.info(f"Verified webhook event: {event['type']}")
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
    def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> str:
        """
        Refund a payment.
        
        Args:
            payment_intent_id: Payment intent ID
            amount: Amount to refund (None = full refund)
            reason: Refund reason
        
        Returns:
            Refund ID
        """
        try:
            refund_params = {"payment_intent": payment_intent_id}
            if amount:
                refund_params["amount"] = amount
            if reason:
                refund_params["reason"] = reason
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(f"Created refund: {refund.id}")
            return refund.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create refund: {e}")
            raise
