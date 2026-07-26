import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from .config import settings

logger = logging.getLogger("mailer")

def send_order_confirmation_email(order_data: dict):
    """
    Sends an automated HTML order confirmation email to the customer.
    Sourced from settings.SMTP_USERNAME (shopnorv@gmail.com).
    """
    # Load configuration
    smtp_server = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(getattr(settings, "SMTP_PORT", 587))
    smtp_username = getattr(settings, "SMTP_USERNAME", "shopnorv@gmail.com")
    # Read password from environment or settings
    smtp_password = getattr(settings, "SMTP_PASSWORD", os.getenv("SMTP_PASSWORD", ""))

    recipient_email = order_data.get("email")
    if not recipient_email:
        logger.error("No recipient email found in order data.")
        return

    if not smtp_password:
        logger.warning("SMTP_PASSWORD is not set. Skipping email dispatch. Please configure App Password for shopnorv@gmail.com.")
        return

    # Build beautiful HTML body
    items_html = ""
    for item in order_data.get("items", []):
        items_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #E5E5E5; color: #1C1C1C;">{item.get('name', 'Product')} ({item.get('size', 'Standard')})</td>
            <td style="padding: 12px; border-bottom: 1px solid #E5E5E5; text-align: center; color: #1C1C1C;">{item.get('quantity', 1)}</td>
            <td style="padding: 12px; border-bottom: 1px solid #E5E5E5; text-align: right; color: #C8A96B; font-weight: bold;">Rs. {item.get('price', 0):,}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #080808;
                color: #FAFAF8;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #FAFAF8;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            }}
            .header {{
                background-color: #080808;
                padding: 40px 20px;
                text-align: center;
                border-bottom: 2px solid #C8A96B;
            }}
            .header h1 {{
                color: #C8A96B;
                font-size: 28px;
                letter-spacing: 4px;
                margin: 0;
                font-weight: 300;
                text-transform: uppercase;
            }}
            .body {{
                padding: 40px 30px;
                color: #1C1C1C;
            }}
            .greeting {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #080808;
            }}
            .intro-text {{
                font-size: 14px;
                color: #6B7280;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .order-details {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            .order-details th {{
                background-color: #080808;
                color: #C8A96B;
                text-align: left;
                padding: 12px;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .total-row {{
                font-size: 16px;
                font-weight: bold;
                background-color: #FAFAF8;
            }}
            .address-box {{
                background-color: #FAFAF8;
                border: 1px solid #E5E5E5;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                color: #1C1C1C;
                font-size: 13px;
                line-height: 1.6;
            }}
            .footer {{
                background-color: #080808;
                padding: 30px 20px;
                text-align: center;
                color: #6B7280;
                font-size: 11px;
                border-top: 1px solid #C8A96B;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>N O R V</h1>
            </div>
            <div class="body">
                <div class="greeting">Thank You For Sourcing With Us</div>
                <p class="intro-text">
                    Hello {order_data.get('name', 'Valued Customer')},<br>
                    Your formulation order #{order_data.get('id', 'N/A')} has been received and confirmed. 
                    We are preparing your package for courier dispatch.
                </p>
                
                <table class="order-details">
                    <thead>
                        <tr>
                            <th>Item Details</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr class="total-row">
                            <td colspan="2" style="padding: 12px; text-align: right; color: #1C1C1C;">Grand Total:</td>
                            <td style="padding: 12px; text-align: right; color: #C8A96B; font-size: 18px;">Rs. {order_data.get('total', 0):,}</td>
                        </tr>
                    </tbody>
                </table>

                <div class="address-box">
                    <strong style="color: #080808; display: block; margin-bottom: 8px; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;">Shipping & Contact Information</strong>
                    <strong>Address:</strong> {order_data.get('address', 'N/A')}, {order_data.get('city', 'N/A')}<br>
                    <strong>Phone:</strong> {order_data.get('phone', 'N/A')}<br>
                    <strong>Payment Method:</strong> {order_data.get('paymentMethod', 'COD')}
                </div>
            </div>
            <div class="footer">
                <p>NORV Atelier Cosmetics — Lahore, Pakistan</p>
                <p>This is an automated order confirmation notification sent from shopnorv@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"NORV: Order Confirmation #{order_data.get('id', 'N/A')}"
    msg["From"] = f"NORV Atelier <{smtp_username}>"
    msg["To"] = recipient_email

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient_email, msg.as_string())
        server.quit()
        logger.info(f"Order confirmation email dispatched successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send order email via SMTP: {str(e)}")
