"""
This script is used to verify the Gmail configuration.
"""

import base64
import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",
]


def gmail_send_message(
    to_email: str,
    from_email: str,
    subject: str = "Automated message",
    content: str = "This is automated mail",
):
    """Create and send an email message.
    Print the returned message id.
    Returns: Message object, including message id.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()

        message.set_content(content)

        message["To"] = to_email
        message["From"] = from_email
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )

        print(f'Message Id: {send_message["id"]}')  # noqa: T201

    except HttpError as error:
        print(f"An error occurred: {error}")  # noqa: T201
        send_message = None

    return send_message


if __name__ == "__main__":
    # Configure your email addresses here
    TO_EMAIL = ""  # Change to your receiver email
    FROM_EMAIL = ""  # Change to your sender Gmail
    SUBJECT = "Test Email"  # Optional: Change the subject
    CONTENT = "This is a test email to verify Gmail configuration"  # Optional: Change the content

    # Validate email configuration
    if not TO_EMAIL or not FROM_EMAIL:
        print(  # noqa: T201
            "Error: Please configure TO_EMAIL and FROM_EMAIL variables before running the script."
        )
        exit(1)

    gmail_send_message(TO_EMAIL, FROM_EMAIL, SUBJECT, CONTENT)
