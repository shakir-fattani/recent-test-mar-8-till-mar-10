"""
Gmail tools.

Refer to the official documents in https://developers.google.com/gmail/api/quickstart/python
"""

import base64
import logging
import os
from email.message import EmailMessage
from typing import Any, ClassVar, Literal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from enterprise_computer_use.tools.base import BaseTool, CLIResult, ToolError

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]


class GmailTool(BaseTool):
    """
    A tool for interacting with Gmail API.
    Supports operations like sending emails.

    Available commands:
        - send: Send an email through Gmail
    """

    name: ClassVar[Literal["gmail"]] = "gmail"

    def __init__(self):
        """Initialize Gmail tool."""
        self._ensure_credentials()
        super().__init__()

    def _ensure_credentials(self) -> None:
        """Ensure valid Gmail credentials are available."""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    raise ToolError("credentials.json file not found")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.creds = creds

    async def __call__(
        self,
        *,
        command: Literal["send"],
        to: str,
        subject: str,
        content: str,
        **kwargs,
    ) -> CLIResult:
        """
        Execute Gmail operations.
        Args:
            command: The operation to perform (send)
            to: Recipient email address
            subject: Email subject
            content: Email content

        Returns:
            CLIResult containing operation output or error
        """
        try:
            if command == "send":
                message_id = self._send_email(to, subject, content)
                return CLIResult(
                    output=f"Email sent successfully. Message ID: {message_id}"
                )

        except Exception as e:
            raise ToolError(f"Gmail operation failed: {str(e)}") from e

    def _send_email(self, to: str, subject: str, content: str) -> str:
        """Send an email using Gmail API."""
        try:
            service = build("gmail", "v1", credentials=self.creds)
            message = EmailMessage()

            message.set_content(content)
            message["To"] = to
            message["Subject"] = subject

            encoded_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()
            create_message = {"raw": encoded_message}

            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            return send_message["id"]  # type: ignore

        except HttpError as e:
            raise ToolError(f"Failed to send email: {str(e)}") from e

    def to_params(self, **kwargs) -> dict[str, Any]:
        """Convert tool to function parameters for LLM."""
        return {
            "name": self.name,
            "description": self.__class__.__doc__,
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["send"],
                        "description": "The Gmail operation to perform",
                    },
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "content": {
                        "type": "string",
                        "description": "Email content",
                    },
                },
                "required": ["command", "to", "subject", "content"],
            },
        }
