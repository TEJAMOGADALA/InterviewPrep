"""Reusable Email Service for PrepOS.

This is the SINGLE entry point for all outbound email — Email Verification,
Forgot Password, and future notification/welcome emails all go through the
functions in this module. Do NOT build a separate email sender for a new
feature; add a template + a thin wrapper function here instead.

Provider: AWS SES via boto3. `boto3` is already a declared project dependency
(see requirements.txt) so this introduces zero new third-party packages.

Dev-mode fallback: if EMAIL_FROM_ADDRESS is not configured, emails are logged
instead of sent, so local development works without real AWS credentials.
This mirrors the existing console-log fallback already used by
routes_auth.forgot_password() for the reset link.

Environment variables:
    EMAIL_FROM_ADDRESS     — verified SES sender, e.g. "PrepOS <no-reply@prepos.io>".
                             Required for real delivery; if unset, dev-mode logging is used.
    AWS_REGION             — SES region, e.g. "us-east-1" (defaults to "us-east-1").
    AWS_ACCESS_KEY_ID       — standard AWS credential (boto3's default credential
    AWS_SECRET_ACCESS_KEY     chain also works, e.g. an IAM role in production).
    FRONTEND_URL            — already used elsewhere in the app; reused here to
                             build absolute links inside email templates.
"""
from __future__ import annotations

import os
import logging
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger("prepos.email")

_APP_NAME = "PrepOS"


# --------------------------------------------------------------------------
# Low-level provider client (AWS SES) — the ONLY code that talks to SES.
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _ses_client():
    """Lazily creates a cached boto3 SES client (avoids reconnecting per email)."""
    import boto3
    region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.client("ses", region_name=region)


def _is_configured() -> bool:
    return bool(os.environ.get("EMAIL_FROM_ADDRESS"))


def send_raw_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """Sends a single email. This is the ONLY function that talks to the email
    provider — every higher-level sender below must go through this.

    Never raises on delivery failure; logs and returns False instead, so a
    transient provider outage can't break the calling request (registration,
    password reset, etc).
    """
    if not to_email:
        return False

    if not _is_configured():
        logger.info(
            "[EMAIL:DEV-MODE] to=%s subject=%r (EMAIL_FROM_ADDRESS not set — "
            "logging instead of sending)\n%s",
            to_email, subject, text_body or html_body,
        )
        return True

    sender = os.environ["EMAIL_FROM_ADDRESS"]
    body = {"Html": {"Data": html_body, "Charset": "UTF-8"}}
    if text_body:
        body["Text"] = {"Data": text_body, "Charset": "UTF-8"}

    try:
        _ses_client().send_email(
            Source=sender,
            Destination={"ToAddresses": [to_email]},
            Message={"Subject": {"Data": subject, "Charset": "UTF-8"}, "Body": body},
        )
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


# --------------------------------------------------------------------------
# Shared HTML layout — every template below renders through this so no
# feature duplicates markup/branding.
# --------------------------------------------------------------------------

def _render_template(
    heading: str,
    body_lines: List[str],
    cta_text: Optional[str] = None,
    cta_link: Optional[str] = None,
) -> str:
    paragraphs = "".join(
        f'<p style="margin:0 0 16px;color:#333;font-size:15px;line-height:1.5;">{line}</p>'
        for line in body_lines
    )
    cta_html = ""
    if cta_text and cta_link:
        cta_html = f"""
        <div style="margin:24px 0;">
          <a href="{cta_link}" style="background:#6d28d9;color:#fff;text-decoration:none;
             padding:12px 24px;border-radius:8px;font-weight:600;font-size:14px;display:inline-block;">
            {cta_text}
          </a>
        </div>"""
    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background:#0b0b12;font-family:-apple-system,Segoe UI,Roboto,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:32px 0;">
      <tr><td align="center">
        <table role="presentation" width="480" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:12px;padding:32px;">
          <tr><td>
            <p style="margin:0 0 20px;font-size:13px;letter-spacing:1px;color:#6d28d9;font-weight:700;">
              {_APP_NAME.upper()}
            </p>
            <h1 style="margin:0 0 16px;font-size:20px;color:#111;">{heading}</h1>
            {paragraphs}
            {cta_html}
            <p style="margin:24px 0 0;color:#999;font-size:12px;">
              If you didn't request this, you can safely ignore this email.
            </p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""


# --------------------------------------------------------------------------
# High-level, feature-specific senders. All funnel through _render_template
# + send_raw_email — no duplicated HTML, no duplicated provider logic.
# None of these are wired into any route yet (foundation only).
# --------------------------------------------------------------------------

def send_verification_email(to_email: str, name: str, verification_link: str) -> bool:
    """Foundation for the future Email Verification flow (not wired up yet)."""
    html = _render_template(
        heading=f"Verify your email, {name}",
        body_lines=[
            "Confirm your email address to finish setting up your PrepOS account.",
            "This link expires shortly for your security.",
        ],
        cta_text="Verify Email",
        cta_link=verification_link,
    )
    text = f"Verify your email: {verification_link}"
    return send_raw_email(to_email, f"Verify your {_APP_NAME} account", html, text)


def send_password_reset_email(to_email: str, name: str, reset_link: str) -> bool:
    """Foundation for the future Forgot Password flow (not wired up yet)."""
    html = _render_template(
        heading="Reset your password",
        body_lines=[
            f"Hi {name}, we received a request to reset your {_APP_NAME} password.",
            "Click below to choose a new one. This link expires shortly for your security.",
        ],
        cta_text="Reset Password",
        cta_link=reset_link,
    )
    text = f"Reset your password: {reset_link}"
    return send_raw_email(to_email, f"Reset your {_APP_NAME} password", html, text)


def send_welcome_email(to_email: str, name: str) -> bool:
    """Reserved for future use — not called anywhere yet."""
    html = _render_template(
        heading=f"Welcome to {_APP_NAME}, {name}!",
        body_lines=["Your account is ready. Let's build your interview prep roadmap."],
        cta_text="Open PrepOS",
        cta_link=os.environ.get("FRONTEND_URL", "http://localhost:3000"),
    )
    return send_raw_email(to_email, f"Welcome to {_APP_NAME}", html)


def send_notification_email(to_email: str, name: str, subject: str, message: str) -> bool:
    """Reserved for future generic notifications (digests, reminders, etc)."""
    html = _render_template(heading=subject, body_lines=[f"Hi {name},", message])
    return send_raw_email(to_email, subject, html, message)
