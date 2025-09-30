"""OAuth2 and SSO provider integration."""

from typing import Dict, Optional
from urllib.parse import urlencode

from authlib.integrations.base_client import OAuthError
from authlib.integrations.requests_client import OAuth2Session


class OAuth2Provider:
    """OAuth2 provider for SSO integration."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        userinfo_url: str,
        redirect_uri: str,
        scopes: Optional[list[str]] = None,
    ):
        """
        Initialize OAuth2 provider.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            authorize_url: Authorization endpoint URL
            token_url: Token endpoint URL
            userinfo_url: User info endpoint URL
            redirect_uri: Redirect URI after auth
            scopes: OAuth scopes
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes or ["openid", "email", "profile"]
    
    def get_authorization_url(self, state: str) -> str:
        """
        Get authorization URL for redirect.
        
        Args:
            state: CSRF state token
        
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        return f"{self.authorize_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
        
        Returns:
            Token response dict
        
        Raises:
            OAuthError: If token exchange fails
        """
        session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
        )
        
        token = session.fetch_token(
            self.token_url,
            code=code,
            grant_type="authorization_code",
        )
        
        return token
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from provider.
        
        Args:
            access_token: OAuth access token
        
        Returns:
            User info dict
        """
        session = OAuth2Session(token={"access_token": access_token})
        response = session.get(self.userinfo_url)
        response.raise_for_status()
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            New token response
        """
        session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        
        token = session.refresh_token(
            self.token_url,
            refresh_token=refresh_token,
        )
        
        return token


class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 provider."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        """Initialize Google OAuth2 provider."""
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
            redirect_uri=redirect_uri,
            scopes=["openid", "email", "profile"],
        )


class MicrosoftOAuth2Provider(OAuth2Provider):
    """Microsoft/Azure AD OAuth2 provider."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        tenant_id: str = "common",
    ):
        """Initialize Microsoft OAuth2 provider."""
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
            token_url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            userinfo_url="https://graph.microsoft.com/v1.0/me",
            redirect_uri=redirect_uri,
            scopes=["openid", "email", "profile"],
        )


class OktaOAuth2Provider(OAuth2Provider):
    """Okta OAuth2 provider."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        okta_domain: str,
    ):
        """Initialize Okta OAuth2 provider."""
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=f"https://{okta_domain}/oauth2/v1/authorize",
            token_url=f"https://{okta_domain}/oauth2/v1/token",
            userinfo_url=f"https://{okta_domain}/oauth2/v1/userinfo",
            redirect_uri=redirect_uri,
            scopes=["openid", "email", "profile"],
        )


def create_oauth_provider(
    provider_name: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    **kwargs,
) -> OAuth2Provider:
    """
    Factory function to create OAuth provider.
    
    Args:
        provider_name: Provider name (google, microsoft, okta, custom)
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: Redirect URI
        **kwargs: Additional provider-specific arguments
    
    Returns:
        OAuth2Provider instance
    """
    providers = {
        "google": GoogleOAuth2Provider,
        "microsoft": MicrosoftOAuth2Provider,
        "okta": OktaOAuth2Provider,
    }
    
    provider_class = providers.get(provider_name.lower())
    
    if provider_class:
        return provider_class(client_id, client_secret, redirect_uri, **kwargs)
    else:
        # Custom provider
        return OAuth2Provider(
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=kwargs["authorize_url"],
            token_url=kwargs["token_url"],
            userinfo_url=kwargs["userinfo_url"],
            redirect_uri=redirect_uri,
            scopes=kwargs.get("scopes"),
        )
