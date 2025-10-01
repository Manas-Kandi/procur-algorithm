"""Integration configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IntegrationConfig(BaseSettings):
    """Integration configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROCUR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Slack
    slack_bot_token: Optional[str] = Field(default=None)
    slack_signing_secret: Optional[str] = Field(default=None)
    slack_app_token: Optional[str] = Field(default=None)
    slack_default_channel: Optional[str] = Field(default=None)
    
    # DocuSign
    docusign_integration_key: Optional[str] = Field(default=None)
    docusign_user_id: Optional[str] = Field(default=None)
    docusign_account_id: Optional[str] = Field(default=None)
    docusign_private_key: Optional[str] = Field(default=None)
    docusign_base_path: str = Field(default="https://demo.docusign.net/restapi")
    docusign_webhook_secret: Optional[str] = Field(default=None)
    
    # ERP
    erp_type: Optional[str] = Field(default="sap")
    sap_base_url: Optional[str] = Field(default=None)
    sap_client_id: Optional[str] = Field(default=None)
    sap_client_secret: Optional[str] = Field(default=None)
    sap_company_code: Optional[str] = Field(default=None)
    
    netsuite_account_id: Optional[str] = Field(default=None)
    netsuite_consumer_key: Optional[str] = Field(default=None)
    netsuite_consumer_secret: Optional[str] = Field(default=None)
    netsuite_token_id: Optional[str] = Field(default=None)
    netsuite_token_secret: Optional[str] = Field(default=None)
    
    # Email
    email_service: str = Field(default="sendgrid")
    sendgrid_api_key: Optional[str] = Field(default=None)
    sendgrid_from_email: Optional[str] = Field(default=None)
    
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    aws_ses_from_email: Optional[str] = Field(default=None)
    
    # Payment
    stripe_api_key: Optional[str] = Field(default=None)
    stripe_webhook_secret: Optional[str] = Field(default=None)
    
    # Storage
    storage_service: str = Field(default="s3")
    s3_bucket_name: Optional[str] = Field(default=None)
    s3_region: str = Field(default="us-east-1")
    google_drive_credentials_file: Optional[str] = Field(default=None)
    
    # Calendar
    calendar_service: str = Field(default="google")
    google_calendar_credentials_file: Optional[str] = Field(default=None)
    outlook_client_id: Optional[str] = Field(default=None)
    outlook_client_secret: Optional[str] = Field(default=None)
    outlook_tenant_id: Optional[str] = Field(default=None)
    outlook_user_email: Optional[str] = Field(default=None)


@lru_cache
def get_integration_config() -> IntegrationConfig:
    """Get cached integration configuration."""
    return IntegrationConfig()
