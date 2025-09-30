#!/usr/bin/env python
"""
Example demonstrating real integrations usage.

This example shows how to use:
1. Slack integration for notifications
2. DocuSign for contract signing
3. ERP integration for purchase orders
4. Email service for notifications
5. Payment processing
6. Document storage
7. Calendar integration
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.integrations.slack_integration import SlackIntegration
from procur.integrations.docusign_integration import DocuSignIntegration
from procur.integrations.erp_integration import SAPIntegration, NetSuiteIntegration
from procur.integrations.email_service import SendGridService, AWSEmailService
from procur.integrations.payment_processors import StripeIntegration
from procur.integrations.storage_service import S3Storage, GoogleDriveStorage
from procur.integrations.calendar_integration import GoogleCalendarIntegration
from procur.integrations.config import get_integration_config


def slack_example():
    """Slack integration example."""
    print("\n" + "="*80)
    print("Slack Integration Example")
    print("="*80)
    
    config = get_integration_config()
    
    if not config.slack_bot_token:
        print("⚠️  Slack not configured. Set PROCUR_SLACK_BOT_TOKEN in .env")
        return
    
    slack = SlackIntegration(
        bot_token=config.slack_bot_token,
        signing_secret=config.slack_signing_secret,
    )
    
    # Send negotiation started notification
    thread_ts = slack.send_negotiation_started(
        channel=config.slack_default_channel or "#procurement",
        negotiation_id="neg-001",
        vendor_name="Salesforce",
        request_description="CRM for 50 users",
        budget=75000.0,
    )
    print(f"✅ Sent negotiation started notification (thread: {thread_ts})")
    
    # Send offer with approval buttons
    slack.send_offer_received(
        channel=config.slack_default_channel or "#procurement",
        thread_ts=thread_ts,
        offer_id="offer-001",
        unit_price=140.0,
        quantity=50,
        term_months=24,
        payment_terms="NET30",
        round_number=1,
    )
    print("✅ Sent offer with interactive approval buttons")


def docusign_example():
    """DocuSign integration example."""
    print("\n" + "="*80)
    print("DocuSign Integration Example")
    print("="*80)
    
    config = get_integration_config()
    
    if not config.docusign_integration_key:
        print("⚠️  DocuSign not configured. Set PROCUR_DOCUSIGN_* variables in .env")
        return
    
    docusign = DocuSignIntegration(
        integration_key=config.docusign_integration_key,
        user_id=config.docusign_user_id,
        account_id=config.docusign_account_id,
        private_key=config.docusign_private_key,
        base_path=config.docusign_base_path,
    )
    
    # Create envelope from document
    envelope_id = docusign.create_envelope_from_document(
        document_path="contract.pdf",
        document_name="Salesforce Contract",
        signer_email="buyer@acme.com",
        signer_name="John Doe",
        subject="Please sign: Salesforce Contract",
    )
    print(f"✅ Created DocuSign envelope: {envelope_id}")
    
    # Check status
    status = docusign.get_envelope_status(envelope_id)
    print(f"   Status: {status['status']}")


def erp_example():
    """ERP integration example."""
    print("\n" + "="*80)
    print("ERP Integration Example")
    print("="*80)
    
    config = get_integration_config()
    
    if config.erp_type == "sap" and config.sap_base_url:
        erp = SAPIntegration(
            base_url=config.sap_base_url,
            client_id=config.sap_client_id,
            client_secret=config.sap_client_secret,
            company_code=config.sap_company_code,
        )
        
        # Validate budget
        budget_check = erp.validate_budget(
            department="IT",
            amount=75000.0,
            fiscal_year=2025,
        )
        print(f"✅ Budget validation:")
        print(f"   Available: {budget_check['available']}")
        print(f"   Budget remaining: ${budget_check['budget_available']:,.2f}")
        
        # Create purchase order
        po_number = erp.create_purchase_order(
            vendor_id="SALESFORCE",
            items=[
                {
                    "material_id": "CRM-LICENSE",
                    "quantity": 50,
                    "unit_price": 140.0,
                    "plant": "1000",
                }
            ],
            total_amount=168000.0,
            currency="USD",
        )
        print(f"✅ Created purchase order: {po_number}")
    else:
        print("⚠️  ERP not configured. Set PROCUR_ERP_TYPE and credentials in .env")


def email_example():
    """Email service example."""
    print("\n" + "="*80)
    print("Email Service Example")
    print("="*80)
    
    config = get_integration_config()
    
    if config.email_service == "sendgrid" and config.sendgrid_api_key:
        email = SendGridService(
            api_key=config.sendgrid_api_key,
            default_from_email=config.sendgrid_from_email,
        )
        
        message_id = email.send_email(
            to_email="buyer@acme.com",
            subject="Negotiation Update",
            html_content="<h1>New offer received</h1><p>Check Slack for details.</p>",
        )
        print(f"✅ Sent email via SendGrid: {message_id}")
    else:
        print("⚠️  Email service not configured. Set PROCUR_SENDGRID_* in .env")


def payment_example():
    """Payment processor example."""
    print("\n" + "="*80)
    print("Payment Processor Example")
    print("="*80)
    
    config = get_integration_config()
    
    if not config.stripe_api_key:
        print("⚠️  Stripe not configured. Set PROCUR_STRIPE_API_KEY in .env")
        return
    
    stripe = StripeIntegration(
        api_key=config.stripe_api_key,
        webhook_secret=config.stripe_webhook_secret,
    )
    
    # Create payment intent
    intent = stripe.create_payment_intent(
        amount=16800000,  # $168,000 in cents
        currency="usd",
        metadata={"contract_id": "contract-001"},
        customer_email="vendor@salesforce.com",
    )
    print(f"✅ Created payment intent: {intent['id']}")
    print(f"   Amount: ${intent['amount']/100:,.2f}")
    print(f"   Status: {intent['status']}")


def storage_example():
    """Document storage example."""
    print("\n" + "="*80)
    print("Document Storage Example")
    print("="*80)
    
    config = get_integration_config()
    
    if config.storage_service == "s3" and config.s3_bucket_name:
        storage = S3Storage(
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            bucket_name=config.s3_bucket_name,
            region_name=config.s3_region,
        )
        
        # Upload contract
        url = storage.upload_file(
            file_path="contract.pdf",
            destination_path="contracts/salesforce-2025.pdf",
            metadata={"contract_id": "contract-001"},
        )
        print(f"✅ Uploaded contract to S3: {url}")
        
        # Generate presigned URL
        presigned_url = storage.generate_presigned_url(
            file_id="contracts/salesforce-2025.pdf",
            expiration=3600,
        )
        print(f"   Presigned URL (1 hour): {presigned_url[:50]}...")
    else:
        print("⚠️  Storage not configured. Set PROCUR_S3_* in .env")


def calendar_example():
    """Calendar integration example."""
    print("\n" + "="*80)
    print("Calendar Integration Example")
    print("="*80)
    
    config = get_integration_config()
    
    if config.calendar_service == "google" and config.google_calendar_credentials_file:
        from google.oauth2.credentials import Credentials
        
        creds = Credentials.from_authorized_user_file(
            config.google_calendar_credentials_file
        )
        
        calendar = GoogleCalendarIntegration(credentials=creds)
        
        # Create contract signing event
        event_id = calendar.create_event(
            summary="Contract Signing: Salesforce",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            description="Sign Salesforce CRM contract",
            attendees=["buyer@acme.com", "legal@acme.com"],
        )
        print(f"✅ Created calendar event: {event_id}")
    else:
        print("⚠️  Calendar not configured. Set PROCUR_GOOGLE_CALENDAR_* in .env")


def main():
    """Run all integration examples."""
    print("=" * 80)
    print("Procur Integrations - Usage Examples")
    print("=" * 80)
    print("\nThese examples demonstrate real integrations with external services.")
    print("Configure credentials in .env to enable each integration.\n")
    
    try:
        slack_example()
    except Exception as e:
        print(f"❌ Slack example failed: {e}")
    
    try:
        docusign_example()
    except Exception as e:
        print(f"❌ DocuSign example failed: {e}")
    
    try:
        erp_example()
    except Exception as e:
        print(f"❌ ERP example failed: {e}")
    
    try:
        email_example()
    except Exception as e:
        print(f"❌ Email example failed: {e}")
    
    try:
        payment_example()
    except Exception as e:
        print(f"❌ Payment example failed: {e}")
    
    try:
        storage_example()
    except Exception as e:
        print(f"❌ Storage example failed: {e}")
    
    try:
        calendar_example()
    except Exception as e:
        print(f"❌ Calendar example failed: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Integration Examples Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Configure credentials in .env for each integration")
    print("2. Test each integration individually")
    print("3. Integrate into your procurement workflows")
    print("\nDocumentation: See INTEGRATIONS_README.md")


if __name__ == "__main__":
    main()
