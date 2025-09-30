"""Email service integrations (SendGrid, AWS SES)."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

logger = logging.getLogger(__name__)


class EmailService(ABC):
    """Base class for email services."""
    
    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Send email."""
        pass


class SendGridService(EmailService):
    """SendGrid email service."""
    
    def __init__(self, api_key: str, default_from_email: str):
        """
        Initialize SendGrid service.
        
        Args:
            api_key: SendGrid API key
            default_from_email: Default sender email
        """
        self.client = SendGridAPIClient(api_key)
        self.default_from_email = default_from_email
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Send email via SendGrid."""
        try:
            message = Mail(
                from_email=from_email or self.default_from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            
            # Add attachments
            if attachments:
                for att in attachments:
                    attachment = Attachment(
                        FileContent(att["content"]),
                        FileName(att["filename"]),
                        FileType(att.get("type", "application/pdf")),
                        Disposition("attachment"),
                    )
                    message.add_attachment(attachment)
            
            response = self.client.send(message)
            logger.info(f"Sent email via SendGrid: {response.status_code}")
            return response.headers.get("X-Message-Id", "")
            
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            raise
    
    def send_template_email(
        self,
        to_email: str,
        template_id: str,
        dynamic_data: Dict[str, Any],
        from_email: Optional[str] = None,
    ) -> str:
        """Send email using SendGrid template."""
        try:
            message = Mail(
                from_email=from_email or self.default_from_email,
                to_emails=to_email,
            )
            message.template_id = template_id
            message.dynamic_template_data = dynamic_data
            
            response = self.client.send(message)
            logger.info(f"Sent template email via SendGrid: {template_id}")
            return response.headers.get("X-Message-Id", "")
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            raise


class AWSEmailService(EmailService):
    """AWS SES email service."""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        default_from_email: str,
    ):
        """
        Initialize AWS SES service.
        
        Args:
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region_name: AWS region
            default_from_email: Default sender email
        """
        self.client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.default_from_email = default_from_email
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Send email via AWS SES."""
        try:
            if attachments:
                # Use raw email for attachments
                return self._send_raw_email(
                    to_email,
                    subject,
                    html_content,
                    from_email,
                    attachments,
                )
            
            response = self.client.send_email(
                Source=from_email or self.default_from_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_content, "Charset": "UTF-8"}
                    },
                },
            )
            
            message_id = response["MessageId"]
            logger.info(f"Sent email via AWS SES: {message_id}")
            return message_id
            
        except ClientError as e:
            logger.error(f"Failed to send email via AWS SES: {e}")
            raise
    
    def _send_raw_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str],
        attachments: List[Dict[str, Any]],
    ) -> str:
        """Send raw email with attachments."""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = from_email or self.default_from_email
        msg["To"] = to_email
        
        # Add HTML body
        msg_body = MIMEMultipart("alternative")
        html_part = MIMEText(html_content, "html", "UTF-8")
        msg_body.attach(html_part)
        msg.attach(msg_body)
        
        # Add attachments
        for att in attachments:
            part = MIMEApplication(att["content"])
            part.add_header("Content-Disposition", "attachment", filename=att["filename"])
            msg.attach(part)
        
        try:
            response = self.client.send_raw_email(
                Source=from_email or self.default_from_email,
                Destinations=[to_email],
                RawMessage={"Data": msg.as_string()},
            )
            
            message_id = response["MessageId"]
            logger.info(f"Sent raw email via AWS SES: {message_id}")
            return message_id
            
        except ClientError as e:
            logger.error(f"Failed to send raw email: {e}")
            raise
