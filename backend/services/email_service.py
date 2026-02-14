"""Email service for PageGuard notifications.
Uses SMTP in production, logs to console in development.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str, text_body: Optional[str] = None):
    """Send an email. Falls back to console logging if SMTP is not configured."""
    if not settings.SMTP_HOST:
        logger.info("EMAIL (dev mode) To: %s | Subject: %s", to, subject)
        logger.debug("Body: %s", text_body or html_body[:200])
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_PORT == 587:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def send_scan_complete_email(to: str, site_url: str, score: int, total_violations: int, site_uid: str):
    """Send scan completion notification."""
    subject = f"PageGuard Scan Complete: {site_url} scored {score}/100"

    if score >= 80:
        score_color = "#16A34A"
        status = "Good"
    elif score >= 50:
        score_color = "#CA8A04"
        status = "Needs Improvement"
    else:
        score_color = "#DC2626"
        status = "Critical"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">PageGuard</h1>
        </div>
        <div style="padding: 24px; background: #fff;">
            <h2 style="margin-top: 0;">Scan Complete for {site_url}</h2>
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 80px; height: 80px; border-radius: 50%; border: 4px solid {score_color}; line-height: 80px; font-size: 28px; font-weight: bold; color: {score_color};">
                    {score}
                </div>
                <p style="color: {score_color}; font-weight: bold; font-size: 18px;">{status}</p>
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Total Violations</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">{total_violations}</td>
                </tr>
            </table>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/dashboard/sites/{site_uid}"
                   style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    View Full Report
                </a>
            </div>
        </div>
        <div style="padding: 16px; text-align: center; color: #6B7280; font-size: 12px;">
            <p>ADA Title II Deadline: April 24, 2026</p>
            <p>&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
        </div>
    </div>
    """

    text = f"Scan complete for {site_url}. Score: {score}/100. Violations: {total_violations}. View report: {settings.FRONTEND_URL}/dashboard/sites/{site_uid}"

    return send_email(to, subject, html, text)


def send_welcome_email(to: str, name: str):
    """Send welcome email after signup."""
    subject = "Welcome to PageGuard - Start Scanning for Free"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">PageGuard</h1>
        </div>
        <div style="padding: 24px; background: #fff;">
            <h2 style="margin-top: 0;">Welcome, {name}!</h2>
            <p>Your PageGuard account is ready. Here's how to get started:</p>
            <ol style="line-height: 1.8;">
                <li><strong>Add your website</strong> - Enter your URL in the dashboard</li>
                <li><strong>Run a free scan</strong> - We'll check for WCAG 2.2 violations</li>
                <li><strong>Get AI fix suggestions</strong> - Exact code changes to fix issues</li>
            </ol>
            <div style="background: #FEF2F2; border: 1px solid #DC2626; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p style="color: #DC2626; font-weight: bold; margin: 0;">
                    ADA Title II Deadline: April 24, 2026
                </p>
                <p style="color: #7F1D1D; margin: 8px 0 0;">
                    Non-compliance penalties up to $150,000 per violation.
                </p>
            </div>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/dashboard"
                   style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Go to Dashboard
                </a>
            </div>
        </div>
        <div style="padding: 16px; text-align: center; color: #6B7280; font-size: 12px;">
            <p>&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
        </div>
    </div>
    """

    text = f"Welcome to PageGuard, {name}! Add your website and run your first free scan at {settings.FRONTEND_URL}/dashboard"

    return send_email(to, subject, html, text)


def send_scan_failed_email(to: str, site_url: str, error_msg: str, site_uid: str):
    """Send notification when a scan fails."""
    subject = f"PageGuard Scan Failed: {site_url}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">PageGuard</h1>
        </div>
        <div style="padding: 24px; background: #fff;">
            <h2 style="margin-top: 0; color: #DC2626;">Scan Failed</h2>
            <p>We were unable to complete a scan for <strong>{site_url}</strong>.</p>
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p style="color: #7F1D1D; margin: 0; font-size: 14px;">
                    <strong>Reason:</strong> {error_msg[:200]}
                </p>
            </div>
            <p style="color: #6B7280;">Common causes: site is offline, firewall blocking our scanner, or the server took too long to respond. You can retry from your dashboard.</p>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/dashboard/sites/{site_uid}"
                   style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Retry Scan
                </a>
            </div>
        </div>
        <div style="padding: 16px; text-align: center; color: #6B7280; font-size: 12px;">
            <p>&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
        </div>
    </div>
    """

    text = f"Scan failed for {site_url}. Reason: {error_msg[:200]}. Retry: {settings.FRONTEND_URL}/dashboard/sites/{site_uid}"
    return send_email(to, subject, html, text)


def send_payment_failed_email(to: str, name: str):
    """Send notification when a payment fails."""
    subject = "PageGuard - Payment Failed"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">PageGuard</h1>
        </div>
        <div style="padding: 24px; background: #fff;">
            <h2 style="margin-top: 0;">Payment Issue</h2>
            <p>Hi {name},</p>
            <p>We were unable to process your latest payment. Please update your payment method to keep your subscription active.</p>
            <div style="background: #FEF3C7; border: 1px solid #FCD34D; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p style="color: #78350F; margin: 0;">
                    Your subscription is now <strong>past due</strong>. Features may be limited until payment is resolved.
                </p>
            </div>
            <div style="text-align: center; margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/dashboard"
                   style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Update Payment
                </a>
            </div>
        </div>
        <div style="padding: 16px; text-align: center; color: #6B7280; font-size: 12px;">
            <p>&copy; 2026 PageGuard. Web accessibility compliance made simple.</p>
        </div>
    </div>
    """

    text = f"Hi {name}, your PageGuard payment failed. Update your payment method at {settings.FRONTEND_URL}/dashboard"
    return send_email(to, subject, html, text)


def send_password_reset_email(to: str, reset_token: str):
    """Send password reset email."""
    subject = "PageGuard - Reset Your Password"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563EB; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">PageGuard</h1>
        </div>
        <div style="padding: 24px; background: #fff;">
            <h2 style="margin-top: 0;">Reset Your Password</h2>
            <p>Click the button below to reset your password. This link expires in 1 hour.</p>
            <div style="text-align: center; margin: 24px 0;">
                <a href="{reset_url}"
                   style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            <p style="color: #6B7280; font-size: 12px;">If you didn't request this, you can safely ignore this email.</p>
        </div>
    </div>
    """

    text = f"Reset your PageGuard password: {reset_url}"

    return send_email(to, subject, html, text)
