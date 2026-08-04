"""
NORV Email Notification System
Sends branded transactional emails via Gmail SMTP
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings

logger = logging.getLogger(__name__)

GOLD = "#C8A96B"
BG   = "#0A0A0A"
CARD = "#111111"
TEXT = "#E5E7EB"
MUTED = "#9CA3AF"

def _base_template(content_html: str, preview_text: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>NORV</title>
</head>
<body style="margin:0;padding:0;background:{BG};font-family:'Helvetica Neue',Arial,sans-serif;">
  {f'<div style="display:none;max-height:0;overflow:hidden;">{preview_text}</div>' if preview_text else ''}
  <table width="100%" cellpadding="0" cellspacing="0" style="background:{BG};padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
        <!-- HEADER -->
        <tr>
          <td style="background:{CARD};border-radius:12px 12px 0 0;padding:32px 40px;text-align:center;border-bottom:2px solid {GOLD};">
            <h1 style="margin:0;font-size:28px;letter-spacing:6px;color:{GOLD};font-weight:300;">NORV</h1>
            <p style="margin:4px 0 0;font-size:11px;letter-spacing:3px;color:{MUTED};text-transform:uppercase;">Atelier</p>
          </td>
        </tr>
        <!-- BODY -->
        <tr>
          <td style="background:{CARD};padding:40px;border-radius:0 0 12px 12px;">
            {content_html}
          </td>
        </tr>
        <!-- FOOTER -->
        <tr>
          <td style="padding:24px 40px;text-align:center;">
            <p style="margin:0;font-size:12px;color:{MUTED};">
              &copy; 2025 NORV Atelier &nbsp;|&nbsp;
              <a href="https://shopnorv.com" style="color:{GOLD};text-decoration:none;">shopnorv.com</a>
            </p>
            <p style="margin:6px 0 0;font-size:11px;color:#4B5563;">
              This is an automated email. Please do not reply directly.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _items_rows(items: list) -> str:
    rows = ""
    for item in items:
        name     = item.get("name", "Product")
        size     = item.get("size", "")
        qty      = item.get("quantity", 1)
        price    = item.get("price", 0)
        subtotal = qty * price
        rows += f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid #1F2937;color:{TEXT};font-size:14px;">
            <strong>{name}</strong><br>
            <span style="color:{MUTED};font-size:12px;">Size: {size} &nbsp;|&nbsp; Qty: {qty}</span>
          </td>
          <td style="padding:12px 0;border-bottom:1px solid #1F2937;color:{GOLD};font-size:14px;text-align:right;font-weight:600;">
            Rs. {subtotal:,}
          </td>
        </tr>"""
    return rows


def _send(to_email: str, subject: str, html: str):
    """Internal helper — opens SMTP connection and sends the email."""
    if not settings.SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD not set — skipping email to %s", to_email)
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"NORV Atelier <{settings.SMTP_USERNAME}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USERNAME, to_email, msg.as_string())

        logger.info("Email sent ✓  to=%s  subject=%s", to_email, subject)

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed — check App Password on Render")
    except Exception as exc:
        logger.error("Email send error: %s", exc)


# ─────────────────────────────────────────────────────────────
# 1. ORDER CONFIRMATION  (sent when order is created)
# ─────────────────────────────────────────────────────────────
def send_order_confirmation_email(order: dict):
    items_html = _items_rows(order.get("items", []))
    total      = order.get("total", 0)
    oid        = order.get("id", "—")
    name       = order.get("name", "Valued Customer")
    address    = order.get("address", "")
    city       = order.get("city", "")
    phone      = order.get("phone", "")
    payment    = order.get("paymentMethod", order.get("payment_method", "COD"))

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      Thank you, <span style="color:{GOLD};">{name}</span>!
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      Your order has been confirmed and is being prepared.
    </p>

    <!-- Order ID Banner -->
    <div style="background:#0D0D0D;border:1px solid {GOLD};border-radius:8px;padding:16px 20px;margin-bottom:28px;text-align:center;">
      <span style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Order ID</span><br>
      <strong style="font-size:20px;color:{GOLD};letter-spacing:1px;">#{oid}</strong>
    </div>

    <!-- Items Table -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
      <tr>
        <td style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;padding-bottom:10px;">Item</td>
        <td style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;padding-bottom:10px;text-align:right;">Amount</td>
      </tr>
      {items_html}
      <tr>
        <td style="padding-top:16px;font-size:16px;font-weight:700;color:{TEXT};">Total</td>
        <td style="padding-top:16px;font-size:18px;font-weight:700;color:{GOLD};text-align:right;">Rs. {total:,}</td>
      </tr>
    </table>

    <!-- Delivery Info -->
    <div style="background:#0D0D0D;border-radius:8px;padding:20px 24px;margin-top:24px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Delivery Details</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📍 {address}, {city}</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📞 {phone}</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">💳 Payment: <strong style="color:{GOLD};">{payment}</strong></p>
    </div>

    <p style="margin:28px 0 0;font-size:13px;color:{MUTED};line-height:1.6;">
      You will receive another email when your order is shipped with tracking details.
      For queries, contact us at
      <a href="mailto:shopnorv@gmail.com" style="color:{GOLD};">shopnorv@gmail.com</a>
    </p>"""

    _send(
        to_email=order.get("email", ""),
        subject=f"NORV: Order Confirmed #{oid} 🛍️",
        html=_base_template(content, preview_text=f"Your NORV order #{oid} is confirmed!")
    )
    
    # Send shop alert notification to admin (shopnorv@gmail.com)
    send_admin_new_order_alert_email(order)


def send_admin_new_order_alert_email(order: dict):
    items_html = _items_rows(order.get("items", []))
    total      = order.get("total", 0)
    oid        = order.get("id", "—")
    name       = order.get("name", "Customer")
    email      = order.get("email", "")
    address    = order.get("address", "")
    city       = order.get("city", "")
    phone      = order.get("phone", "")
    payment    = order.get("paymentMethod", order.get("payment_method", "COD"))
    notes      = order.get("customer_notes", order.get("customerNotes", "")) or "No notes"

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:#EF4444;font-weight:400;">
      🚨 New Order Received!
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      An order has been placed on the storefront. Details below:
    </p>

    <!-- Order ID Banner -->
    <div style="background:#0D0D0D;border:1px solid {GOLD};border-radius:8px;padding:16px 20px;margin-bottom:28px;text-align:center;">
      <span style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Order ID</span><br>
      <strong style="font-size:20px;color:{GOLD};letter-spacing:1px;">#{oid}</strong>
    </div>

    <!-- Items Table -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
      <tr>
        <td style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;padding-bottom:10px;">Item</td>
        <td style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;padding-bottom:10px;text-align:right;">Amount</td>
      </tr>
      {items_html}
      <tr>
        <td style="padding-top:16px;font-size:16px;font-weight:700;color:{TEXT};">Total Revenue</td>
        <td style="padding-top:16px;font-size:18px;font-weight:700;color:{GOLD};text-align:right;">Rs. {total:,}</td>
      </tr>
    </table>

    <!-- Customer Details -->
    <div style="background:#0D0D0D;border-radius:8px;padding:20px 24px;margin-top:24px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Customer Profile</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">👤 Name: <strong>{name}</strong> ({email})</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📍 Address: {address}, {city}</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📞 Phone: {phone}</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">💳 Method: <strong style="color:{GOLD};">{payment}</strong></p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📝 Notes: <em>{notes}</em></p>
    </div>

    <div style="margin-top:24px;text-align:center;">
      <a href="https://admin.shopnorv.com" style="display:inline-block;background:{GOLD};color:#000;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;letter-spacing:1px;">
        OPEN ADMIN PANEL
      </a>
    </div>"""

    _send(
        to_email=settings.SMTP_USERNAME, # Send directly to shopnorv@gmail.com
        subject=f"🚨 [New Order] #{oid} - Rs. {total:,} by {name}",
        html=_base_template(content, preview_text=f"New order #{oid} has been placed!")
    )



# ─────────────────────────────────────────────────────────────
# 2. ORDER SHIPPED  (sent when status → Shipped)
# ─────────────────────────────────────────────────────────────
def send_order_shipped_email(order: dict):
    oid      = order.get("id", "—")
    name     = order.get("name", "Valued Customer")
    tracking = order.get("tracking_number", "") or order.get("trackingNumber", "")
    city     = order.get("city", "")
    eta      = order.get("estimated_delivery", "") or order.get("estimatedDelivery", "3-5 Working Days")

    tracking_html = f"""
    <div style="background:#0D0D0D;border:1px solid {GOLD};border-radius:8px;padding:16px 20px;margin:20px 0;text-align:center;">
      <span style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Tracking Number</span><br>
      <strong style="font-size:18px;color:{GOLD};">{tracking}</strong>
    </div>""" if tracking and tracking not in ("Not Dispatched", "—", "") else ""

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      Your order is on its way, <span style="color:{GOLD};">{name}</span>!
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      Your NORV order has been shipped and is heading to you.
    </p>

    <div style="background:#0D0D0D;border-radius:8px;padding:20px 24px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Shipment Details</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📦 Order ID: <strong style="color:{GOLD};">#{oid}</strong></p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">🏙️ Delivering to: <strong>{city}</strong></p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">🕐 Estimated: <strong>{eta}</strong></p>
    </div>

    {tracking_html}

    <p style="margin:28px 0 0;font-size:13px;color:{MUTED};line-height:1.6;">
      For any queries, reach us at
      <a href="mailto:shopnorv@gmail.com" style="color:{GOLD};">shopnorv@gmail.com</a>
    </p>"""

    _send(
        to_email=order.get("email", ""),
        subject=f"NORV: Your Order #{oid} Has Been Shipped 🚚",
        html=_base_template(content, preview_text=f"Your NORV order #{oid} is on the way!")
    )


# ─────────────────────────────────────────────────────────────
# 3. OUT FOR DELIVERY  (sent when status → Out for Delivery)
# ─────────────────────────────────────────────────────────────
def send_out_for_delivery_email(order: dict):
    oid  = order.get("id", "—")
    name = order.get("name", "Valued Customer")
    city = order.get("city", "")

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      Almost there, <span style="color:{GOLD};">{name}</span>!
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      Your NORV order is <strong style="color:{GOLD};">out for delivery</strong> today.
    </p>

    <div style="background:#0D0D0D;border-radius:8px;padding:20px 24px;text-align:center;">
      <div style="font-size:48px;margin-bottom:12px;">🛵</div>
      <p style="margin:0;color:{TEXT};font-size:16px;font-weight:600;">Order #{oid}</p>
      <p style="margin:8px 0 0;color:{MUTED};font-size:14px;">Delivering to {city} today</p>
    </div>

    <p style="margin:28px 0 0;font-size:13px;color:{MUTED};line-height:1.6;">
      Please ensure someone is available to receive the package.
      Contact us at <a href="mailto:shopnorv@gmail.com" style="color:{GOLD};">shopnorv@gmail.com</a> for help.
    </p>"""

    _send(
        to_email=order.get("email", ""),
        subject=f"NORV: Order #{oid} Out for Delivery Today! 🛵",
        html=_base_template(content, preview_text=f"Your NORV order is arriving today!")
    )


# ─────────────────────────────────────────────────────────────
# 4. DELIVERED  (sent when status → Delivered)
# ─────────────────────────────────────────────────────────────
def send_order_delivered_email(order: dict):
    oid  = order.get("id", "—")
    name = order.get("name", "Valued Customer")

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      Delivered! We hope you love it, <span style="color:{GOLD};">{name}</span> 💛
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      Your NORV order <strong style="color:{GOLD};">#{oid}</strong> has been delivered.
    </p>

    <div style="background:#0D0D0D;border-radius:8px;padding:24px;text-align:center;">
      <div style="font-size:48px;margin-bottom:12px;">✅</div>
      <p style="margin:0;color:{GOLD};font-size:18px;font-weight:600;">Order Delivered Successfully</p>
      <p style="margin:10px 0 0;color:{MUTED};font-size:13px;">
        We would love to hear your feedback. Leave a review on our website!
      </p>
    </div>

    <div style="margin-top:24px;text-align:center;">
      <a href="https://shopnorv.com" style="display:inline-block;background:{GOLD};color:#000;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;letter-spacing:1px;">
        SHOP AGAIN
      </a>
    </div>

    <p style="margin:28px 0 0;font-size:13px;color:{MUTED};line-height:1.6;">
      Thank you for choosing NORV Atelier. ✨<br>
      For support: <a href="mailto:shopnorv@gmail.com" style="color:{GOLD};">shopnorv@gmail.com</a>
    </p>"""

    _send(
        to_email=order.get("email", ""),
        subject=f"NORV: Order #{oid} Delivered! Thank You 💛",
        html=_base_template(content, preview_text=f"Your NORV order has been delivered!")
    )


# ─────────────────────────────────────────────────────────────
# 5. SUBSCRIBER CONFIRMATION  (sent when user signs up for launch notify)
# ─────────────────────────────────────────────────────────────
def send_subscriber_confirmation_email(email: str, source: str):
    source_label = source or "NORV Newsletter"

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      You're on the list! <span style="color:{GOLD};">✓</span>
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      Thank you for subscribing to NORV Atelier updates.
    </p>

    <!-- Confirmation Banner -->
    <div style="background:#0D0D0D;border:1px solid {GOLD};border-radius:8px;padding:24px;margin-bottom:28px;text-align:center;">
      <span style="font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Subscription Confirmed</span><br>
      <strong style="font-size:20px;color:{GOLD};letter-spacing:1px;">NORV Atelier</strong>
    </div>

    <div style="background:#0D0D0D;border-radius:8px;padding:20px 24px;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">What to expect:</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📦 Be first to know when new collections launch.</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">🎯 Exclusive early access and launch pricing.</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">✨ Premium grooming tips crafted for Pakistani men.</p>
    </div>

    <div style="margin-top:24px;text-align:center;">
      <a href="https://shopnorv.com" style="display:inline-block;background:{GOLD};color:#000;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;letter-spacing:1px;">
        BROWSE NORV STORE
      </a>
    </div>

    <p style="margin:28px 0 0;font-size:13px;color:{MUTED};line-height:1.6;">
      Thank you for being part of NORV Atelier. ✨<br>
      For queries: <a href="mailto:shopnorv@gmail.com" style="color:{GOLD};">shopnorv@gmail.com</a>
    </p>"""

    _send(
        to_email=email,
        subject="NORV: You're subscribed! Welcome to the Atelier 🎯",
        html=_base_template(content, preview_text="Your NORV newsletter subscription is confirmed!")
    )


def send_admin_new_subscriber_alert_email(email: str, source: str, total_subscribers: int):
    source_label = source or "Footer Newsletter"

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:#10B981;font-weight:400;">
      🔔 New Subscriber!
    </h2>
    <p style="margin:0 0 28px;color:{MUTED};font-size:14px;">
      A new visitor has subscribed to NORV updates.
    </p>

    <div style="background:#0D0D0D;border:1px solid {GOLD};border-radius:8px;padding:20px 24px;margin-bottom:20px;">
      <p style="margin:0 0 10px;font-size:11px;letter-spacing:2px;color:{MUTED};text-transform:uppercase;">Subscriber Details</p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📧 Email: <strong style="color:{GOLD};">{email}</strong></p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">📍 Source: <strong>{source_label}</strong></p>
      <p style="margin:4px 0;color:{TEXT};font-size:14px;">👥 Total Subscribers: <strong style="color:{GOLD};">{total_subscribers}</strong></p>
    </div>

    <div style="margin-top:24px;text-align:center;">
      <a href="https://admin.shopnorv.com" style="display:inline-block;background:{GOLD};color:#000;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;letter-spacing:1px;">
        VIEW IN ADMIN PANEL
      </a>
    </div>"""

    _send(
        to_email=settings.SMTP_USERNAME,
        subject=f"🔔 [New Subscriber] {email} — via {source_label} ({total_subscribers} total)",
        html=_base_template(content, preview_text=f"New subscriber: {email}")
    )
