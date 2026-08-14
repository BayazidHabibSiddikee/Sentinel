import smtplib
import json
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Add project root to path so database can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import database


def _get_email_config() -> dict:
    """Retrieve email configuration from the database."""
    return {
        "sender": database.get_state("EMAIL_SENDER", ""),
        "password": database.get_state("EMAIL_PASSWORD", ""),
        "smtp_host": database.get_state("EMAIL_SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(database.get_state("EMAIL_SMTP_PORT", 587)),
        "display_name": database.get_state("EMAIL_DISPLAY_NAME", "Sentinel — RUET Study Platform"),
    }


def get_contacts() -> list:
    """Return the saved contact list (students + teachers)."""
    raw = database.get_state("EMAIL_CONTACTS", [])
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return []


def save_contacts(contacts: list) -> None:
    """Persist the contact list."""
    database.set_state("EMAIL_CONTACTS", contacts)


def lookup_contact(query: str) -> dict | None:
    """Find a contact by name or email (case-insensitive)."""
    q = query.strip().lower()
    for c in get_contacts():
        if q in c.get("name", "").lower() or q in c.get("email", "").lower():
            return c
    return None


def _build_html_body(body: str, sender_name: str) -> str:
    """Wrap plain text body in a styled HTML email template."""
    # Convert newlines to <br> for HTML
    html_body = body.replace("\n", "<br>")
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0d1117; color: #e6edf3; margin: 0; padding: 0; }}
  .wrapper {{ max-width: 600px; margin: 32px auto; background: #161b22; border: 1px solid #30363d; border-radius: 10px; overflow: hidden; }}
  .header {{ background: linear-gradient(135deg, #1c2128 0%, #0d1117 100%); padding: 24px 32px; border-bottom: 1px solid #30363d; }}
  .header .brand {{ font-size: 1.1rem; font-weight: 700; color: #58a6ff; letter-spacing: 0.08em; }}
  .header .sub {{ font-size: 0.75rem; color: #8b949e; margin-top: 2px; }}
  .body {{ padding: 28px 32px; font-size: 0.95rem; line-height: 1.7; color: #c9d1d9; }}
  .footer {{ padding: 16px 32px; border-top: 1px solid #30363d; font-size: 0.72rem; color: #6e7681; }}
</style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="brand">⚔️ SENTINEL</div>
      <div class="sub">RUET AI Academic Platform</div>
    </div>
    <div class="body">
      {html_body}
    </div>
    <div class="footer">
      Sent via Sentinel — AI Academic Weapon for RUET &nbsp;|&nbsp; {sender_name}
    </div>
  </div>
</body>
</html>"""


def send_email(
    recipient_email: str,
    subject: str,
    body: str,
    cc: str = "",
    reply_to: str = "",
    html: bool = True,
) -> str:
    """
    Send an email using the SMTP config stored in the database.

    Args:
        recipient_email: Target email address (or comma-separated list)
        subject: Email subject line
        body: Email body (plain text; auto-converted to HTML if html=True)
        cc: Optional CC addresses (comma-separated)
        reply_to: Optional reply-to address
        html: Whether to send as HTML (default True)

    Returns:
        A string describing the result.
    """
    cfg = _get_email_config()

    if not cfg["sender"]:
        return "❌ Failed: Sender email is not configured. Go to Settings → Email tab."
    if not cfg["password"]:
        return "❌ Failed: Email app password is not configured. Go to Settings → Email tab."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f'{cfg["display_name"]} <{cfg["sender"]}>'
        msg["To"] = recipient_email
        if cc:
            msg["Cc"] = cc
        if reply_to:
            msg["Reply-To"] = reply_to

        # Plain text fallback
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if html:
            html_content = _build_html_body(body, cfg["display_name"])
            msg.attach(MIMEText(html_content, "html", "utf-8"))

        all_recipients = [r.strip() for r in recipient_email.split(",") if r.strip()]
        if cc:
            all_recipients += [r.strip() for r in cc.split(",") if r.strip()]

        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["sender"], cfg["password"])
            server.sendmail(cfg["sender"], all_recipients, msg.as_string())

        recipients_str = ", ".join(all_recipients[:3])
        if len(all_recipients) > 3:
            recipients_str += f" + {len(all_recipients) - 3} more"
        return f"✅ Email sent successfully to {recipients_str}."

    except smtplib.SMTPAuthenticationError:
        return "❌ Authentication failed. Check your email and app password in Settings → Email tab."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {e}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"


# ── Agentic alias (keeps backward compatibility) ─────────────────────────────
def send_email_agentic(recipient_email: str, subject: str, body: str) -> str:
    return send_email(recipient_email, subject, body)
