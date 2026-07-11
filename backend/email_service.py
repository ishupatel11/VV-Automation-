"""
email_service.py — Gmail SMTP email sender with premium Black & White HTML template.
"""

import smtplib
import ssl
import json
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

from config import get_settings
from logger import get_logger

log = get_logger(__name__)
settings = get_settings()

IST = timezone(timedelta(hours=5, minutes=30))
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def _build_html_email(
    full_name: str,
    email: str,
    subject: str,
    message: str,
    ip_address: str,
    submitted_at: datetime,
) -> str:
    """Return a premium Black & White HTML email body."""
    submitted_ist = submitted_at.replace(tzinfo=timezone.utc).astimezone(IST)
    timestamp = submitted_ist.strftime("%d %b %Y  •  %I:%M %p IST")

    def esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
        )

    initials = "".join(w[0].upper() for w in full_name.strip().split()[:2])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>New Contact Submission — V.V. Automation</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background:#0a0a0a;padding:52px 20px;">
    <tr>
      <td align="center" valign="top">

        <!-- Outer glow ring -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;width:100%;border-radius:20px;overflow:hidden;
                      box-shadow:0 0 0 1px rgba(255,255,255,0.1),
                                 0 32px 80px rgba(0,0,0,0.9);">

          <!-- ══ TOP ACCENT BAR ══ -->
          <tr>
            <td style="background:linear-gradient(90deg,#111,#fff,#111);height:2px;font-size:0;line-height:0;">
              &nbsp;
            </td>
          </tr>

          <!-- ══ HEADER ══ -->
          <tr>
            <td style="background:#111111;padding:44px 48px 36px;text-align:center;
                        border-bottom:1px solid rgba(255,255,255,0.07);">

              <!-- Logo mark -->
              <div style="display:inline-block;width:60px;height:60px;border-radius:16px;
                          background:#ffffff;text-align:center;line-height:60px;
                          font-size:24px;margin-bottom:20px;
                          box-shadow:0 0 30px rgba(255,255,255,0.15);">
                ✉
              </div>

              <h1 style="margin:0 0 8px;font-size:24px;font-weight:700;
                          color:#ffffff;letter-spacing:-0.5px;line-height:1.2;">
                New Contact Enquiry
              </h1>
              <p style="margin:0;font-size:12px;color:#555555;
                         text-transform:uppercase;letter-spacing:2px;font-weight:500;">
                V.V. Automation &nbsp;·&nbsp; Contact Form
              </p>
            </td>
          </tr>

          <!-- ══ BODY ══ -->
          <tr>
            <td style="background:#111111;padding:36px 48px 0;">

              <!-- Sender row -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:32px;">
                <tr>
                  <!-- Initials avatar -->
                  <td width="54" valign="middle">
                    <div style="width:50px;height:50px;border-radius:12px;
                                background:#ffffff;color:#000000;
                                font-size:17px;font-weight:800;
                                text-align:center;line-height:50px;
                                letter-spacing:0.5px;">
                      {esc(initials)}
                    </div>
                  </td>
                  <td style="padding-left:16px;" valign="middle">
                    <p style="margin:0 0 4px;font-size:18px;font-weight:700;color:#ffffff;
                               letter-spacing:-0.3px;">
                      {esc(full_name)}
                    </p>
                    <p style="margin:0;font-size:13px;color:#888888;">
                      {esc(email)}
                    </p>
                  </td>
                  <td align="right" valign="middle">
                    <span style="display:inline-block;background:transparent;
                                  border:1px solid rgba(255,255,255,0.25);
                                  color:#ffffff;font-size:10px;font-weight:700;
                                  padding:5px 14px;border-radius:20px;
                                  letter-spacing:1.5px;text-transform:uppercase;">
                      NEW
                    </span>
                  </td>
                </tr>
              </table>

              <!-- Hair line -->
              <div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:32px;"></div>

              <!-- Subject field -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:28px;">
                <tr>
                  <td style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);
                              border-radius:12px;padding:16px 20px;">
                    <p style="margin:0 0 5px;font-size:10px;font-weight:700;
                               color:#555555;text-transform:uppercase;letter-spacing:2px;">
                      Subject
                    </p>
                    <p style="margin:0;font-size:16px;font-weight:600;color:#ffffff;">
                      {esc(subject)}
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Message field -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:32px;">
                <tr>
                  <td>
                    <p style="margin:0 0 10px;font-size:10px;font-weight:700;
                               color:#555555;text-transform:uppercase;letter-spacing:2px;">
                      Message
                    </p>
                    <!-- Left border accent — white -->
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td width="3" style="background:#ffffff;border-radius:2px;font-size:0;">&nbsp;</td>
                        <td style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);
                                    border-left:none;border-radius:0 12px 12px 0;padding:20px 24px;">
                          <p style="margin:0;font-size:15px;color:#cccccc;line-height:1.85;
                                     white-space:pre-wrap;font-style:italic;">
                            "{esc(message)}"
                          </p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Hair line -->
              <div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:28px;"></div>

              <!-- Meta 2-col -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:36px;">
                <tr>
                  <td width="49%" style="padding-right:6px;">
                    <div style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);
                                 border-radius:12px;padding:16px 18px;">
                      <p style="margin:0 0 6px;font-size:10px;font-weight:700;color:#555555;
                                 text-transform:uppercase;letter-spacing:1.8px;">
                        Submitted
                      </p>
                      <p style="margin:0;font-size:13px;color:#aaaaaa;font-weight:500;">
                        {timestamp}
                      </p>
                    </div>
                  </td>
                  <td width="2%"></td>
                  <td width="49%" style="padding-left:6px;">
                    <div style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);
                                 border-radius:12px;padding:16px 18px;">
                      <p style="margin:0 0 6px;font-size:10px;font-weight:700;color:#555555;
                                 text-transform:uppercase;letter-spacing:1.8px;">
                        IP Address
                      </p>
                      <p style="margin:0;font-size:13px;color:#aaaaaa;font-weight:500;">
                        {esc(ip_address)}
                      </p>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:44px;">
                <tr>
                  <td align="center">
                    <a href="mailto:{esc(email)}?subject=Re%3A%20{esc(subject)}"
                       style="display:inline-block;background:#ffffff;color:#000000;
                               text-decoration:none;padding:16px 44px;
                               border-radius:12px;font-weight:800;font-size:15px;
                               letter-spacing:0.3px;
                               box-shadow:0 0 40px rgba(255,255,255,0.12);">
                      Reply to {esc(full_name)} &nbsp;→
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- ══ BOTTOM ACCENT BAR ══ -->
          <tr>
            <td style="background:linear-gradient(90deg,#111,#fff,#111);height:1px;font-size:0;line-height:0;">
              &nbsp;
            </td>
          </tr>

          <!-- ══ FOOTER ══ -->
          <tr>
            <td style="background:#0d0d0d;padding:22px 48px;text-align:center;">
              <p style="margin:0 0 4px;font-size:12px;color:#333333;font-weight:600;
                         text-transform:uppercase;letter-spacing:1.5px;">
                V.V. Automation
              </p>
              <p style="margin:0;font-size:11px;color:#2a2a2a;">
                Automated notification — reply directly to the sender using the button above.
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>
"""


def send_contact_email(
    full_name: str,
    email: str,
    subject: str,
    message: str,
    ip_address: str,
    submitted_at: datetime,
) -> None:
    """
    Send an HTML notification email.
    Uses Resend API (HTTP POST) if RESEND_API_KEY is configured.
    Otherwise, falls back to Gmail SMTP (SSL, port 465).
    """
    html_body = _build_html_email(
        full_name=full_name,
        email=email,
        subject=subject,
        message=message,
        ip_address=ip_address,
        submitted_at=submitted_at,
    )

    if settings.RESEND_API_KEY:
        log.info("Sending email via Resend API...")
        # Note: If domain is not verified, Resend requires 'from' to be 'onboarding@resend.dev'
        payload = {
            "from": "VV Automation <onboarding@resend.dev>",
            "to": settings.RECIPIENT_EMAIL,
            "subject": f"[VV Automation] New Enquiry: {subject}",
            "html": html_body,
            "reply_to": email
        }
        
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=req_data,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": f"VVAutomation-ContactAPI/1.0"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10.0) as response:
                resp_body = response.read().decode("utf-8")
                log.info("Email sent successfully via Resend API | response=%s", resp_body)
                return
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            log.error("Resend API HTTP error | code=%d | response=%s", err.code, err_body)
            raise Exception(f"Resend API error: {err_body}") from err
        except Exception as exc:
            log.error("Failed to send email via Resend API | error=%s", exc)
            raise

    # Fallback to Gmail SMTP
    log.info("Sending email via Gmail SMTP...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[VV Automation] New Enquiry: {subject}"
    msg["From"]    = f"VV Automation Website <{settings.GMAIL_USER}>"
    msg["To"]      = settings.RECIPIENT_EMAIL
    msg["Reply-To"] = email

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=15.0) as server:
            server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
            server.sendmail(
                from_addr=settings.GMAIL_USER,
                to_addrs=[settings.RECIPIENT_EMAIL],
                msg=msg.as_string(),
            )
        log.info(
            "Email sent successfully via SMTP | to=%s | subject=%s",
            settings.RECIPIENT_EMAIL, subject,
        )
    except smtplib.SMTPAuthenticationError:
        log.error(
            "Gmail SMTP authentication failed. "
            "Check GMAIL_USER and GMAIL_APP_PASSWORD in your .env file."
        )
        raise
    except Exception as exc:
        log.error("Failed to send email via SMTP | error=%s", exc)
        raise
