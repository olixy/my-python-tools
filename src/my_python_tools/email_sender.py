"""
Email sending module supporting Brevo and Gmail.

Credentials are loaded automatically from the .env file in the
my-python-tools project root. Required variables:

  Brevo:  BREVO_API_KEY, BREVO_SENDER_EMAIL
  Gmail:  GMAIL_ADDRESS, GMAIL_APP_PASSWORD

Set EMAIL_PROVIDER to "brevo" (default) or "gmail" to choose the backend.
"""

import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

_BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
_GMAIL_SMTP_SERVER = "smtp.gmail.com"
_GMAIL_SMTP_PORT = 587


def _send_via_brevo(to, subject, body):
    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")

    if not api_key:
        raise RuntimeError("BREVO_API_KEY is not set in my-python-tools/.env")
    if not sender_email:
        raise RuntimeError("BREVO_SENDER_EMAIL is not set in my-python-tools/.env")

    response = requests.post(
        _BREVO_API_URL,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={
            "sender": {"email": sender_email},
            "to": [{"email": to}],
            "subject": subject,
            "textContent": body,
        },
        timeout=15,
    )

    if not response.ok:
        raise RuntimeError(f"Brevo API error {response.status_code}: {response.text}")


def _send_via_gmail(to, subject, body):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address:
        raise RuntimeError("GMAIL_ADDRESS is not set in my-python-tools/.env")
    if not gmail_password:
        raise RuntimeError("GMAIL_APP_PASSWORD is not set in my-python-tools/.env")

    message = MIMEText(body, "plain", "utf-8")
    message["From"] = gmail_address
    message["To"] = to
    message["Subject"] = subject

    try:
        with smtplib.SMTP(_GMAIL_SMTP_SERVER, _GMAIL_SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(gmail_address, gmail_password)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            "SMTP authentication failed. Verify GMAIL_ADDRESS and GMAIL_APP_PASSWORD."
        ) from exc


_PROVIDERS = {
    "brevo": _send_via_brevo,
    "gmail": _send_via_gmail,
}


def send_email(to, subject, body, provider=None):
    """Send a plain-text email.

    provider: "brevo" or "gmail". Falls back to EMAIL_PROVIDER env var, then "brevo".
    """
    if provider is None:
        provider = os.environ.get("EMAIL_PROVIDER", "brevo").lower()

    fn = _PROVIDERS.get(provider)
    if fn is None:
        raise RuntimeError(
            f"Unknown email provider '{provider}'. Choose 'brevo' or 'gmail'."
        )

    fn(to, subject, body)
