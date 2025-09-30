"""Real Slack integration with webhooks, interactive buttons, and thread management."""

import logging
from typing import Any, Dict, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Real Slack integration for notifications and approvals."""
    
    def __init__(
        self,
        bot_token: str,
        signing_secret: str,
        app_token: Optional[str] = None,
    ):
        """
        Initialize Slack integration.
        
        Args:
            bot_token: Slack bot token (xoxb-...)
            signing_secret: Slack signing secret for webhook verification
            app_token: Slack app token for Socket Mode (optional)
        """
        self.client = WebClient(token=bot_token)
        self.verifier = SignatureVerifier(signing_secret)
        self.app_token = app_token
    
    def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Channel ID or name
            text: Message text (fallback)
            blocks: Block Kit blocks for rich formatting
            thread_ts: Thread timestamp to reply in thread
        
        Returns:
            Response dict with ts (timestamp) for threading
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts,
            )
            logger.info(f"Sent message to {channel}: {response['ts']}")
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to send Slack message: {e.response['error']}")
            raise
    
    def send_negotiation_started(
        self,
        channel: str,
        negotiation_id: str,
        vendor_name: str,
        request_description: str,
        budget: float,
    ) -> str:
        """
        Send negotiation started notification.
        
        Returns:
            Thread timestamp for follow-up messages
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤝 Negotiation Started with {vendor_name}",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Negotiation ID:*\n{negotiation_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Budget:*\n${budget:,.2f}"
                    },
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Request:*\n{request_description}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Updates will be posted in this thread"
                    }
                ]
            }
        ]
        
        response = self.send_message(channel, f"Negotiation started with {vendor_name}", blocks)
        return response["ts"]
    
    def send_offer_received(
        self,
        channel: str,
        thread_ts: str,
        offer_id: str,
        unit_price: float,
        quantity: int,
        term_months: int,
        payment_terms: str,
        round_number: int,
    ) -> str:
        """
        Send offer received notification with approval buttons.
        
        Returns:
            Message timestamp
        """
        total_value = unit_price * quantity * term_months
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📨 New Offer Received (Round {round_number})*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Unit Price:*\n${unit_price:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity:*\n{quantity}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Term:*\n{term_months} months"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Payment:*\n{payment_terms}"
                    },
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Contract Value:* ${total_value:,.2f}"
                }
            },
            {
                "type": "actions",
                "block_id": f"offer_actions_{offer_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": offer_id,
                        "action_id": "approve_offer"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": offer_id,
                        "action_id": "reject_offer"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "💬 Counter"
                        },
                        "value": offer_id,
                        "action_id": "counter_offer"
                    }
                ]
            }
        ]
        
        response = self.send_message(
            channel,
            f"New offer received: ${unit_price:,.2f}/unit",
            blocks,
            thread_ts,
        )
        return response["ts"]
    
    def send_approval_request(
        self,
        channel: str,
        user_ids: List[str],
        request_id: str,
        description: str,
        budget: float,
        vendor_name: str,
    ) -> str:
        """
        Send approval request with mentions.
        
        Args:
            user_ids: List of Slack user IDs to mention
            
        Returns:
            Message timestamp
        """
        mentions = " ".join([f"<@{uid}>" for uid in user_ids])
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔔 Approval Required*\n{mentions}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Request ID:*\n{request_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Vendor:*\n{vendor_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Budget:*\n${budget:,.2f}"
                    },
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description}"
                }
            },
            {
                "type": "actions",
                "block_id": f"approval_actions_{request_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": request_id,
                        "action_id": "approve_request"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": request_id,
                        "action_id": "reject_request"
                    }
                ]
            }
        ]
        
        response = self.send_message(
            channel,
            f"Approval required for {request_id}",
            blocks,
        )
        return response["ts"]
    
    def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
    ):
        """Update an existing message."""
        try:
            self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks,
            )
            logger.info(f"Updated message {ts} in {channel}")
        except SlackApiError as e:
            logger.error(f"Failed to update message: {e.response['error']}")
            raise
    
    def add_reaction(self, channel: str, ts: str, reaction: str):
        """Add emoji reaction to a message."""
        try:
            self.client.reactions_add(
                channel=channel,
                timestamp=ts,
                name=reaction,
            )
        except SlackApiError as e:
            logger.error(f"Failed to add reaction: {e.response['error']}")
    
    def send_contract_ready(
        self,
        channel: str,
        thread_ts: str,
        contract_id: str,
        vendor_name: str,
        total_value: float,
        document_url: str,
    ) -> str:
        """Send contract ready notification."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📄 Contract Ready for Signature*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Contract ID:*\n{contract_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Vendor:*\n{vendor_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Value:*\n${total_value:,.2f}"
                    },
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📝 Sign Contract"
                        },
                        "style": "primary",
                        "url": document_url,
                        "action_id": "sign_contract"
                    }
                ]
            }
        ]
        
        response = self.send_message(
            channel,
            f"Contract ready: {contract_id}",
            blocks,
            thread_ts,
        )
        return response["ts"]
    
    def verify_request(self, timestamp: str, signature: str, body: str) -> bool:
        """
        Verify Slack request signature.
        
        Args:
            timestamp: X-Slack-Request-Timestamp header
            signature: X-Slack-Signature header
            body: Raw request body
        
        Returns:
            True if signature is valid
        """
        return self.verifier.is_valid(body, timestamp, signature)
    
    def handle_interaction(self, payload: Dict) -> Dict[str, Any]:
        """
        Handle interactive component (button click).
        
        Args:
            payload: Interaction payload from Slack
        
        Returns:
            Response dict with action details
        """
        action = payload["actions"][0]
        action_id = action["action_id"]
        value = action["value"]
        user = payload["user"]
        
        logger.info(f"Interaction: {action_id} by {user['username']} for {value}")
        
        return {
            "action_id": action_id,
            "value": value,
            "user_id": user["id"],
            "username": user["username"],
            "channel_id": payload["channel"]["id"],
            "message_ts": payload["message"]["ts"],
        }
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information."""
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e.response['error']}")
            raise
    
    def create_channel(self, name: str, is_private: bool = False) -> str:
        """
        Create a new channel.
        
        Returns:
            Channel ID
        """
        try:
            if is_private:
                response = self.client.conversations_create(
                    name=name,
                    is_private=True,
                )
            else:
                response = self.client.conversations_create(name=name)
            
            channel_id = response["channel"]["id"]
            logger.info(f"Created channel: {name} ({channel_id})")
            return channel_id
        except SlackApiError as e:
            logger.error(f"Failed to create channel: {e.response['error']}")
            raise
    
    def invite_users(self, channel: str, user_ids: List[str]):
        """Invite users to a channel."""
        try:
            self.client.conversations_invite(
                channel=channel,
                users=",".join(user_ids),
            )
            logger.info(f"Invited {len(user_ids)} users to {channel}")
        except SlackApiError as e:
            logger.error(f"Failed to invite users: {e.response['error']}")
            raise
