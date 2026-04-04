"""Ultron — Email notification delivery via SendGrid/Resend."""

import logging
from backend.config import settings
from backend.utils.brand import BRAND_NAME, WEBSITE, EMAIL

logger = logging.getLogger(__name__)


def send_email_alert(priority: str, title: str, message: str, to_email: str = None):
    """Send alert email. Uses SendGrid if configured, else logs."""
    recipient = to_email or EMAIL

    # Try SendGrid
    sendgrid_key = getattr(settings, "SENDGRID_API_KEY", "")
    if sendgrid_key:
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content

            sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
            emoji = {"critical": "🔴", "important": "🟡"}.get(priority, "🔵")
            mail = Mail(
                from_email=Email(EMAIL, BRAND_NAME),
                to_emails=To(recipient),
                subject=f"{emoji} Ultron Alert: {title}",
                html_content=Content("text/html", f"""
                    <div style="font-family:Arial;max-width:600px;margin:0 auto">
                        <div style="background:#003235;color:white;padding:20px;text-align:center">
                            <h2>{BRAND_NAME} — Ultron Empire</h2>
                        </div>
                        <div style="padding:20px;background:#F5F7FA">
                            <h3 style="color:#003235">{emoji} {title}</h3>
                            <p style="white-space:pre-wrap">{message}</p>
                        </div>
                        <div style="padding:15px;text-align:center;font-size:12px;color:#999">
                            {BRAND_NAME} | {WEBSITE}
                        </div>
                    </div>
                """),
            )
            sg.client.mail.send.post(request_body=mail.get())
            logger.info(f"Email sent to {recipient}: {title}")
            return
        except Exception as e:
            logger.error(f"SendGrid email failed: {e}")

    logger.info(f"Email alert (no provider): [{priority}] {title} → {recipient}")
