"""
Quick SMTP debug endpoint - remove after testing
"""
from fastapi import APIRouter
from ..mailer import send_order_confirmation_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

router = APIRouter(prefix="/api/debug", tags=["Debug"])

@router.get("/smtp-test")
def test_smtp():
    """Test SMTP connection and send a test email"""
    result = {}
    
    result["smtp_server"] = settings.SMTP_SERVER
    result["smtp_port"] = settings.SMTP_PORT
    result["smtp_username"] = settings.SMTP_USERNAME
    result["smtp_password_set"] = len(settings.SMTP_PASSWORD) > 0
    result["smtp_password_length"] = len(settings.SMTP_PASSWORD)
    
    if not settings.SMTP_PASSWORD:
        result["error"] = "SMTP_PASSWORD is empty! Set it on Render."
        return result
    
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10)
        server.set_debuglevel(0)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "NORV SMTP Test - Working!"
        msg["From"] = f"NORV Atelier <{settings.SMTP_USERNAME}>"
        msg["To"] = "arsalansidhu28@gmail.com"
        msg.attach(MIMEText(
            "<h2 style='color:#C8A96B'>NORV Email System is Working!</h2><p>Yeh test email hai — system live hai.</p>",
            "html"
        ))
        
        server.sendmail(settings.SMTP_USERNAME, "arsalansidhu28@gmail.com", msg.as_string())
        server.quit()
        
        result["status"] = "SUCCESS - Email sent to arsalansidhu28@gmail.com"
        
    except smtplib.SMTPAuthenticationError as e:
        result["error"] = f"AUTH FAILED: {str(e)} — App Password galat hai ya spaces hain"
    except smtplib.SMTPException as e:
        result["error"] = f"SMTP ERROR: {str(e)}"
    except Exception as e:
        result["error"] = f"GENERAL ERROR: {str(e)}"
    
    return result


@router.get("/trace-order-creation")
def trace_order_creation():
    """Manually test mailer formatting directly to see if it throws error"""
    try:
        order_data = {
            "id": "N-DEBUG-999",
            "name": "Arsalan Debug",
            "email": "arsalansidhu28@gmail.com",
            "phone": "+923220017592",
            "address": "Mandi Usman Wala",
            "city": "Lahore",
            "paymentMethod": "COD",
            "total": 1200,
            "items": [
                {
                    "productId": 1,
                    "name": "OUD Mist Body Wash",
                    "quantity": 1,
                    "size": "100ml",
                    "price": 1200
                }
            ]
        }
        send_order_confirmation_email(order_data)
        return {"status": "Mailer formatted successfully"}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

