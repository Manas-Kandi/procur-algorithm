# Procur Integrations

## Overview

Comprehensive real integrations with external services for Slack notifications, DocuSign e-signatures, ERP systems, email, payments, storage, and calendars.

## Features

✅ **Slack Integration** - Webhooks, interactive buttons, thread management, user mentions
✅ **DocuSign Integration** - API authentication, envelope creation, webhooks, templates
✅ **ERP Integration** - SAP, NetSuite connectors with PO creation, budget validation
✅ **Email Service** - SendGrid, AWS SES with templates and attachments
✅ **Payment Processing** - Stripe integration with webhooks
✅ **Document Storage** - S3, Google Drive with presigned URLs
✅ **Calendar Integration** - Google Calendar, Outlook with event management
✅ **SSO Providers** - Already implemented in auth module (Okta, Auth0, Azure AD)

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

New dependencies:
- `slack-sdk>=3.26` - Slack API client
- `docusign-esign>=3.25` - DocuSign SDK
- `sendgrid>=6.11` - SendGrid email
- `boto3>=1.34` - AWS services (SES, S3)
- `stripe>=7.0` - Stripe payments
- `google-api-python-client>=2.108` - Google APIs
- `msal>=1.26` - Microsoft authentication
- `okta>=2.9` - Okta SDK

### 2. Configure Integrations

Update `.env` with your credentials:

```env
# Slack
PROCUR_SLACK_BOT_TOKEN=xoxb-your-token
PROCUR_SLACK_SIGNING_SECRET=your-secret
PROCUR_SLACK_DEFAULT_CHANNEL=#procurement

# DocuSign
PROCUR_DOCUSIGN_INTEGRATION_KEY=your-key
PROCUR_DOCUSIGN_USER_ID=your-user-id
PROCUR_DOCUSIGN_ACCOUNT_ID=your-account-id
PROCUR_DOCUSIGN_PRIVATE_KEY=your-private-key

# ERP (SAP)
PROCUR_ERP_TYPE=sap
PROCUR_SAP_BASE_URL=https://your-sap-instance.com
PROCUR_SAP_CLIENT_ID=your-client-id
PROCUR_SAP_CLIENT_SECRET=your-secret
PROCUR_SAP_COMPANY_CODE=1000

# Email (SendGrid)
PROCUR_EMAIL_SERVICE=sendgrid
PROCUR_SENDGRID_API_KEY=SG.your-api-key
PROCUR_SENDGRID_FROM_EMAIL=noreply@procur.ai

# Stripe
PROCUR_STRIPE_API_KEY=sk_test_your-key
PROCUR_STRIPE_WEBHOOK_SECRET=whsec_your-secret

# S3
PROCUR_STORAGE_SERVICE=s3
PROCUR_S3_BUCKET_NAME=procur-documents
PROCUR_AWS_ACCESS_KEY_ID=your-key
PROCUR_AWS_SECRET_ACCESS_KEY=your-secret
```

### 3. Test Integrations

```bash
python examples/integrations_example.py
```

## Slack Integration

### Features
- Send rich messages with Block Kit
- Interactive approval buttons
- Thread management for negotiations
- User mentions and notifications
- Webhook verification
- Real-time updates

### Usage

```python
from procur.integrations.slack_integration import SlackIntegration

slack = SlackIntegration(
    bot_token="xoxb-your-token",
    signing_secret="your-secret",
)

# Send negotiation started
thread_ts = slack.send_negotiation_started(
    channel="#procurement",
    negotiation_id="neg-001",
    vendor_name="Salesforce",
    request_description="CRM for 50 users",
    budget=75000.0,
)

# Send offer with approval buttons
slack.send_offer_received(
    channel="#procurement",
    thread_ts=thread_ts,
    offer_id="offer-001",
    unit_price=140.0,
    quantity=50,
    term_months=24,
    payment_terms="NET30",
    round_number=1,
)

# Handle button click
interaction = slack.handle_interaction(payload)
if interaction["action_id"] == "approve_offer":
    # Process approval
    pass
```

### Setup

1. Create Slack app at https://api.slack.com/apps
2. Add OAuth scopes: `chat:write`, `reactions:write`, `users:read`
3. Install app to workspace
4. Copy Bot Token and Signing Secret
5. Configure webhook URL for interactivity

## DocuSign Integration

### Features
- JWT authentication
- Create envelopes from documents
- Use reusable templates
- Track signing status
- Download signed documents
- Webhook verification
- Void envelopes

### Usage

```python
from procur.integrations.docusign_integration import DocuSignIntegration

docusign = DocuSignIntegration(
    integration_key="your-key",
    user_id="your-user-id",
    account_id="your-account-id",
    private_key="your-private-key",
)

# Create envelope from document
envelope_id = docusign.create_envelope_from_document(
    document_path="contract.pdf",
    document_name="Salesforce Contract",
    signer_email="buyer@acme.com",
    signer_name="John Doe",
    subject="Please sign: Salesforce Contract",
)

# Check status
status = docusign.get_envelope_status(envelope_id)
print(f"Status: {status['status']}")

# Download signed document
if status['status'] == 'completed':
    docs = docusign.get_envelope_documents(envelope_id)
    with open("signed_contract.pdf", "wb") as f:
        f.write(docs)
```

### Setup

1. Create DocuSign developer account
2. Create integration key
3. Generate RSA keypair
4. Grant consent for app
5. Configure webhook URL for Connect

## ERP Integration

### Supported Systems
- SAP (OData API)
- NetSuite (REST API)
- Oracle (extensible)

### Features
- Create purchase orders
- Validate budgets
- Create invoices
- Reconcile invoices with POs
- 3-way matching

### Usage - SAP

```python
from procur.integrations.erp_integration import SAPIntegration

erp = SAPIntegration(
    base_url="https://your-sap.com",
    client_id="your-client-id",
    client_secret="your-secret",
    company_code="1000",
)

# Validate budget
budget_check = erp.validate_budget(
    department="IT",
    amount=75000.0,
    fiscal_year=2025,
)

if budget_check['available']:
    # Create PO
    po_number = erp.create_purchase_order(
        vendor_id="SALESFORCE",
        items=[
            {
                "material_id": "CRM-LICENSE",
                "quantity": 50,
                "unit_price": 140.0,
            }
        ],
        total_amount=168000.0,
    )
```

### Usage - NetSuite

```python
from procur.integrations.erp_integration import NetSuiteIntegration

erp = NetSuiteIntegration(
    account_id="your-account",
    consumer_key="your-key",
    consumer_secret="your-secret",
    token_id="your-token-id",
    token_secret="your-token-secret",
)

# Same API as SAP
po_number = erp.create_purchase_order(...)
```

## Email Service

### Providers
- SendGrid
- AWS SES

### Features
- HTML emails
- Attachments
- Templates
- Batch sending

### Usage - SendGrid

```python
from procur.integrations.email_service import SendGridService

email = SendGridService(
    api_key="SG.your-key",
    default_from_email="noreply@procur.ai",
)

# Send email
message_id = email.send_email(
    to_email="buyer@acme.com",
    subject="Negotiation Update",
    html_content="<h1>New offer</h1>",
    attachments=[
        {
            "content": pdf_bytes,
            "filename": "offer.pdf",
            "type": "application/pdf",
        }
    ],
)

# Send template email
email.send_template_email(
    to_email="buyer@acme.com",
    template_id="d-template-id",
    dynamic_data={"vendor_name": "Salesforce"},
)
```

### Usage - AWS SES

```python
from procur.integrations.email_service import AWSEmailService

email = AWSEmailService(
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret",
    region_name="us-east-1",
    default_from_email="noreply@procur.ai",
)

# Same API as SendGrid
message_id = email.send_email(...)
```

## Payment Processing

### Stripe Integration

```python
from procur.integrations.payment_processors import StripeIntegration

stripe = StripeIntegration(
    api_key="sk_test_your-key",
    webhook_secret="whsec_your-secret",
)

# Create payment intent
intent = stripe.create_payment_intent(
    amount=16800000,  # $168,000 in cents
    currency="usd",
    metadata={"contract_id": "contract-001"},
)

# Create customer
customer_id = stripe.create_customer(
    email="vendor@salesforce.com",
    name="Salesforce Inc",
)

# Create subscription
subscription = stripe.create_subscription(
    customer_id=customer_id,
    price_id="price_monthly",
)

# Verify webhook
event = stripe.verify_webhook(payload, signature)
if event['type'] == 'payment_intent.succeeded':
    # Handle successful payment
    pass
```

## Document Storage

### Providers
- AWS S3
- Google Drive
- SharePoint (extensible)

### Usage - S3

```python
from procur.integrations.storage_service import S3Storage

storage = S3Storage(
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret",
    bucket_name="procur-documents",
    region_name="us-east-1",
)

# Upload file
url = storage.upload_file(
    file_path="contract.pdf",
    destination_path="contracts/salesforce-2025.pdf",
    metadata={"contract_id": "contract-001"},
)

# Generate presigned URL (temporary access)
presigned_url = storage.generate_presigned_url(
    file_id="contracts/salesforce-2025.pdf",
    expiration=3600,  # 1 hour
)

# List files
files = storage.list_files(folder_id="contracts/")

# Download file
storage.download_file(
    file_id="contracts/salesforce-2025.pdf",
    destination_path="downloaded.pdf",
)
```

### Usage - Google Drive

```python
from procur.integrations.storage_service import GoogleDriveStorage
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file("credentials.json")
storage = GoogleDriveStorage(credentials=creds)

# Upload file
file_id = storage.upload_file(
    file_path="contract.pdf",
    destination_path="Salesforce Contract 2025.pdf",
    folder_id="folder-id",
)

# Share file
storage.share_file(
    file_id=file_id,
    email="legal@acme.com",
    role="reader",
)
```

## Calendar Integration

### Providers
- Google Calendar
- Outlook/Microsoft 365

### Usage - Google Calendar

```python
from procur.integrations.calendar_integration import GoogleCalendarIntegration
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

creds = Credentials.from_authorized_user_file("credentials.json")
calendar = GoogleCalendarIntegration(credentials=creds)

# Create event
event_id = calendar.create_event(
    summary="Contract Signing: Salesforce",
    start_time=datetime.utcnow() + timedelta(days=1),
    end_time=datetime.utcnow() + timedelta(days=1, hours=1),
    description="Sign Salesforce CRM contract",
    attendees=["buyer@acme.com", "legal@acme.com"],
)

# Update event
calendar.update_event(
    event_id=event_id,
    updates={"summary": "Contract Signing: Salesforce (Updated)"},
)
```

### Usage - Outlook

```python
from procur.integrations.calendar_integration import OutlookCalendarIntegration

calendar = OutlookCalendarIntegration(
    client_id="your-client-id",
    client_secret="your-secret",
    tenant_id="your-tenant-id",
    user_email="user@company.com",
)

# Same API as Google Calendar
event_id = calendar.create_event(...)
```

## Integration Workflows

### Complete Procurement Flow

```python
from procur.integrations import *

# 1. Send Slack notification
slack.send_negotiation_started(...)

# 2. Validate budget in ERP
budget_check = erp.validate_budget(...)

# 3. Send email notification
email.send_email(...)

# 4. Create calendar event
calendar.create_event(...)

# 5. Generate contract in DocuSign
envelope_id = docusign.create_envelope_from_document(...)

# 6. Upload to S3
storage.upload_file(...)

# 7. Process payment
stripe.create_payment_intent(...)

# 8. Create PO in ERP
po_number = erp.create_purchase_order(...)
```

## Webhook Handlers

### Slack Webhook

```python
from fastapi import Request

@app.post("/webhooks/slack")
async def slack_webhook(request: Request):
    # Verify signature
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    body = await request.body()
    
    if not slack.verify_request(timestamp, signature, body.decode()):
        return {"error": "Invalid signature"}
    
    # Handle interaction
    payload = json.loads(request.form.get("payload"))
    interaction = slack.handle_interaction(payload)
    
    # Process action
    if interaction["action_id"] == "approve_offer":
        # Approve offer logic
        pass
    
    return {"ok": True}
```

### DocuSign Webhook

```python
@app.post("/webhooks/docusign")
async def docusign_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-DocuSign-Signature-1")
    payload = await request.json()
    
    if not docusign.verify_webhook(payload, signature, webhook_secret):
        return {"error": "Invalid signature"}
    
    # Handle event
    event = docusign.handle_webhook(payload)
    
    if event["event"] == "envelope-completed":
        # Download signed document
        docs = docusign.get_envelope_documents(event["envelope_id"])
        # Store in S3
        storage.upload_file(...)
    
    return {"ok": True}
```

### Stripe Webhook

```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    event = stripe.verify_webhook(payload, signature)
    
    if event["type"] == "payment_intent.succeeded":
        # Handle successful payment
        pass
    
    return {"ok": True}
```

## Best Practices

1. **Secure Credentials**: Store in environment variables, never commit
2. **Verify Webhooks**: Always verify signatures
3. **Handle Errors**: Implement retry logic
4. **Rate Limiting**: Respect API rate limits
5. **Logging**: Log all integration calls
6. **Testing**: Use sandbox/test environments
7. **Monitoring**: Track integration health

## Troubleshooting

### Slack Issues
- Verify bot token starts with `xoxb-`
- Check OAuth scopes
- Ensure app is installed to workspace

### DocuSign Issues
- Use demo environment for testing
- Verify JWT configuration
- Check user consent

### ERP Issues
- Verify API credentials
- Check network connectivity
- Validate data formats

### Email Issues
- Verify sender email is verified
- Check spam filters
- Monitor bounce rates

## Support

- **Documentation**: This file
- **Examples**: `examples/integrations_example.py`
- **Configuration**: `.env.example`
- **Issues**: GitHub Issues

## License

Part of the Procur procurement automation platform.
