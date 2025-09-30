"""Calendar integrations (Google Calendar, Outlook)."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class GoogleCalendarIntegration:
    """Google Calendar integration."""
    
    def __init__(self, credentials: Credentials):
        """Initialize Google Calendar integration."""
        self.service = build("calendar", "v3", credentials=credentials)
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary",
    ) -> str:
        """
        Create calendar event.
        
        Returns:
            Event ID
        """
        try:
            event = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
            }
            
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]
            
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates="all",
            ).execute()
            
            event_id = result["id"]
            logger.info(f"Created Google Calendar event: {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            raise
    
    def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Get calendar event."""
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id,
            ).execute()
            return event
        except Exception as e:
            logger.error(f"Failed to get calendar event: {e}")
            raise
    
    def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        calendar_id: str = "primary",
    ):
        """Update calendar event."""
        try:
            event = self.get_event(event_id, calendar_id)
            event.update(updates)
            
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates="all",
            ).execute()
            
            logger.info(f"Updated calendar event: {event_id}")
        except Exception as e:
            logger.error(f"Failed to update calendar event: {e}")
            raise
    
    def delete_event(self, event_id: str, calendar_id: str = "primary"):
        """Delete calendar event."""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates="all",
            ).execute()
            logger.info(f"Deleted calendar event: {event_id}")
        except Exception as e:
            logger.error(f"Failed to delete calendar event: {e}")
            raise


class OutlookCalendarIntegration:
    """Outlook/Microsoft 365 Calendar integration."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        user_email: str,
    ):
        """Initialize Outlook Calendar integration."""
        self.client_id = client_id
        self.user_email = user_email
        
        self.app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret,
        )
        
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Get access token."""
        result = self.app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Failed to get access token: {result.get('error_description')}")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> str:
        """Create calendar event."""
        import requests
        
        try:
            event = {
                "subject": summary,
                "body": {
                    "contentType": "HTML",
                    "content": description or "",
                },
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
            }
            
            if attendees:
                event["attendees"] = [
                    {
                        "emailAddress": {"address": email},
                        "type": "required",
                    }
                    for email in attendees
                ]
            
            response = requests.post(
                f"https://graph.microsoft.com/v1.0/users/{self.user_email}/calendar/events",
                json=event,
                headers=self._headers(),
            )
            response.raise_for_status()
            
            event_id = response.json()["id"]
            logger.info(f"Created Outlook event: {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to create Outlook event: {e}")
            raise
