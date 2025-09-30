"""Real DocuSign integration with API, webhooks, and template management."""

import base64
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from docusign_esign import (
    ApiClient,
    EnvelopesApi,
    TemplatesApi,
    Document,
    Signer,
    SignHere,
    Tabs,
    Recipients,
    EnvelopeDefinition,
)
from docusign_esign.client.api_exception import ApiException

logger = logging.getLogger(__name__)


class DocuSignIntegration:
    """Real DocuSign integration for contract signing."""
    
    def __init__(
        self,
        integration_key: str,
        user_id: str,
        account_id: str,
        private_key: str,
        base_path: str = "https://demo.docusign.net/restapi",
    ):
        """
        Initialize DocuSign integration.
        
        Args:
            integration_key: DocuSign integration key
            user_id: DocuSign user ID (GUID)
            account_id: DocuSign account ID
            private_key: RSA private key for JWT
            base_path: API base path (demo or production)
        """
        self.integration_key = integration_key
        self.user_id = user_id
        self.account_id = account_id
        self.private_key = private_key
        self.base_path = base_path
        
        # Initialize API client
        self.api_client = ApiClient()
        self.api_client.host = base_path
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate using JWT."""
        try:
            # Request JWT token
            response = self.api_client.request_jwt_user_token(
                client_id=self.integration_key,
                user_id=self.user_id,
                oauth_host_name="account-d.docusign.com",
                private_key_bytes=self.private_key.encode(),
                expires_in=3600,
            )
            
            # Set access token
            self.api_client.set_default_header(
                "Authorization",
                f"Bearer {response.access_token}"
            )
            
            logger.info("DocuSign authentication successful")
        except ApiException as e:
            logger.error(f"DocuSign authentication failed: {e}")
            raise
    
    def create_envelope_from_document(
        self,
        document_path: str,
        document_name: str,
        signer_email: str,
        signer_name: str,
        subject: str,
        email_subject: Optional[str] = None,
        cc_recipients: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Create envelope from document file.
        
        Args:
            document_path: Path to PDF document
            document_name: Document name
            signer_email: Signer email address
            signer_name: Signer full name
            subject: Envelope subject
            email_subject: Email subject (optional)
            cc_recipients: List of CC recipients
        
        Returns:
            Envelope ID
        """
        try:
            # Read document
            with open(document_path, "rb") as file:
                content_bytes = file.read()
            
            base64_file_content = base64.b64encode(content_bytes).decode("ascii")
            
            # Create document
            document = Document(
                document_base64=base64_file_content,
                name=document_name,
                file_extension="pdf",
                document_id="1",
            )
            
            # Create signer
            signer = Signer(
                email=signer_email,
                name=signer_name,
                recipient_id="1",
                routing_order="1",
            )
            
            # Add signature tab
            sign_here = SignHere(
                document_id="1",
                page_number="1",
                x_position="100",
                y_position="100",
            )
            
            signer.tabs = Tabs(sign_here_tabs=[sign_here])
            
            # Create recipients
            recipients = Recipients(signers=[signer])
            
            # Add CC recipients
            if cc_recipients:
                from docusign_esign import CarbonCopy
                cc_list = []
                for i, cc in enumerate(cc_recipients, start=2):
                    cc_list.append(CarbonCopy(
                        email=cc["email"],
                        name=cc["name"],
                        recipient_id=str(i),
                        routing_order=str(i),
                    ))
                recipients.carbon_copies = cc_list
            
            # Create envelope
            envelope_definition = EnvelopeDefinition(
                email_subject=email_subject or subject,
                documents=[document],
                recipients=recipients,
                status="sent",
            )
            
            # Send envelope
            envelopes_api = EnvelopesApi(self.api_client)
            results = envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition,
            )
            
            envelope_id = results.envelope_id
            logger.info(f"Created DocuSign envelope: {envelope_id}")
            return envelope_id
            
        except ApiException as e:
            logger.error(f"Failed to create envelope: {e}")
            raise
    
    def create_envelope_from_template(
        self,
        template_id: str,
        signer_email: str,
        signer_name: str,
        template_roles: Optional[List[Dict[str, Any]]] = None,
        subject: str = "Please sign this document",
    ) -> str:
        """
        Create envelope from template.
        
        Args:
            template_id: DocuSign template ID
            signer_email: Signer email
            signer_name: Signer name
            template_roles: List of template roles with data
            subject: Email subject
        
        Returns:
            Envelope ID
        """
        try:
            from docusign_esign import TemplateRole
            
            # Create template role
            if not template_roles:
                template_roles = [
                    {
                        "email": signer_email,
                        "name": signer_name,
                        "role_name": "Signer",
                    }
                ]
            
            roles = []
            for role_data in template_roles:
                role = TemplateRole(
                    email=role_data["email"],
                    name=role_data["name"],
                    role_name=role_data["role_name"],
                )
                
                # Add tabs data if provided
                if "tabs" in role_data:
                    role.tabs = role_data["tabs"]
                
                roles.append(role)
            
            # Create envelope
            envelope_definition = EnvelopeDefinition(
                email_subject=subject,
                template_id=template_id,
                template_roles=roles,
                status="sent",
            )
            
            envelopes_api = EnvelopesApi(self.api_client)
            results = envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition,
            )
            
            envelope_id = results.envelope_id
            logger.info(f"Created envelope from template: {envelope_id}")
            return envelope_id
            
        except ApiException as e:
            logger.error(f"Failed to create envelope from template: {e}")
            raise
    
    def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get envelope status."""
        try:
            envelopes_api = EnvelopesApi(self.api_client)
            envelope = envelopes_api.get_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id,
            )
            
            return {
                "envelope_id": envelope_id,
                "status": envelope.status,
                "created_date": envelope.created_date_time,
                "sent_date": envelope.sent_date_time,
                "completed_date": envelope.completed_date_time,
                "email_subject": envelope.email_subject,
            }
        except ApiException as e:
            logger.error(f"Failed to get envelope status: {e}")
            raise
    
    def get_envelope_documents(self, envelope_id: str) -> bytes:
        """Download signed documents."""
        try:
            envelopes_api = EnvelopesApi(self.api_client)
            documents = envelopes_api.get_document(
                account_id=self.account_id,
                envelope_id=envelope_id,
                document_id="combined",
            )
            
            logger.info(f"Downloaded documents for envelope: {envelope_id}")
            return documents
        except ApiException as e:
            logger.error(f"Failed to download documents: {e}")
            raise
    
    def void_envelope(self, envelope_id: str, reason: str):
        """Void an envelope."""
        try:
            from docusign_esign import Envelope
            
            envelope = Envelope(voided_reason=reason)
            
            envelopes_api = EnvelopesApi(self.api_client)
            envelopes_api.update(
                account_id=self.account_id,
                envelope_id=envelope_id,
                envelope=envelope,
            )
            
            logger.info(f"Voided envelope: {envelope_id}")
        except ApiException as e:
            logger.error(f"Failed to void envelope: {e}")
            raise
    
    def get_recipient_status(self, envelope_id: str) -> List[Dict[str, Any]]:
        """Get recipient signing status."""
        try:
            envelopes_api = EnvelopesApi(self.api_client)
            recipients = envelopes_api.list_recipients(
                account_id=self.account_id,
                envelope_id=envelope_id,
            )
            
            status_list = []
            for signer in recipients.signers or []:
                status_list.append({
                    "name": signer.name,
                    "email": signer.email,
                    "status": signer.status,
                    "signed_date": signer.signed_date_time,
                    "delivered_date": signer.delivered_date_time,
                })
            
            return status_list
        except ApiException as e:
            logger.error(f"Failed to get recipient status: {e}")
            raise
    
    def create_template(
        self,
        template_name: str,
        document_path: str,
        document_name: str,
        roles: List[Dict[str, str]],
    ) -> str:
        """
        Create a reusable template.
        
        Args:
            template_name: Template name
            document_path: Path to document
            document_name: Document name
            roles: List of roles (name, role_name)
        
        Returns:
            Template ID
        """
        try:
            # Read document
            with open(document_path, "rb") as file:
                content_bytes = file.read()
            
            base64_file_content = base64.b64encode(content_bytes).decode("ascii")
            
            # Create document
            document = Document(
                document_base64=base64_file_content,
                name=document_name,
                file_extension="pdf",
                document_id="1",
            )
            
            # Create signers from roles
            from docusign_esign import Signer as TemplateSigner
            signers = []
            for i, role in enumerate(roles, start=1):
                signer = TemplateSigner(
                    role_name=role["role_name"],
                    recipient_id=str(i),
                    routing_order=str(i),
                )
                signers.append(signer)
            
            # Create envelope template
            from docusign_esign import EnvelopeTemplate
            template = EnvelopeTemplate(
                name=template_name,
                documents=[document],
                recipients=Recipients(signers=signers),
                email_subject=f"Please sign: {template_name}",
            )
            
            templates_api = TemplatesApi(self.api_client)
            results = templates_api.create_template(
                account_id=self.account_id,
                envelope_template=template,
            )
            
            template_id = results.template_id
            logger.info(f"Created template: {template_id}")
            return template_id
            
        except ApiException as e:
            logger.error(f"Failed to create template: {e}")
            raise
    
    def verify_webhook(self, payload: Dict, hmac_signature: str, secret: str) -> bool:
        """
        Verify DocuSign Connect webhook signature.
        
        Args:
            payload: Webhook payload
            hmac_signature: X-DocuSign-Signature-1 header
            secret: Webhook secret
        
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        import json
        
        # Compute HMAC
        message = json.dumps(payload, separators=(",", ":")).encode()
        computed_hmac = base64.b64encode(
            hmac.new(secret.encode(), message, hashlib.sha256).digest()
        ).decode()
        
        return hmac.compare_digest(computed_hmac, hmac_signature)
    
    def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        """
        Handle DocuSign Connect webhook.
        
        Args:
            payload: Webhook payload
        
        Returns:
            Processed event data
        """
        event = payload.get("event")
        envelope_id = payload.get("data", {}).get("envelopeId")
        
        logger.info(f"DocuSign webhook: {event} for envelope {envelope_id}")
        
        return {
            "event": event,
            "envelope_id": envelope_id,
            "status": payload.get("data", {}).get("envelopeSummary", {}).get("status"),
            "timestamp": payload.get("generated"),
        }
