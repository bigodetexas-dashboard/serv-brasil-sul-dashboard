import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


def send_2fa_code(email, code):
    """
    Sends a real 2FA code via SMTP.
    Returns: (success: bool, message: str)
    """
    if not SMTP_USER or not SMTP_PASS:
        print("[EMAIL] ⚠️ SMTP credentials missing in .env. Falling back to Mock.")
        print(f"[MOCK EMAIL] To: {email} | Code: {code}")
        return True, "Email sent (mock - credentials missing)"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Código de Acesso: {code} - BigodeTexas"
        msg["From"] = f"BigodeTexas Security <{SMTP_FROM}>"
        msg["To"] = email

        # HTML Template
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; border-top: 5px solid #ff6b00;">
              <h1 style="color: #333; text-align: center;">🛡️ Verificação de Segurança</h1>
              <p style="color: #666; font-size: 16px;">Olá,</p>
              <p style="color: #666; font-size: 16px;">Seu código de verificação para acessar o Painel Admin do BigodeTexas é:</p>
              <div style="background-color: #eee; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #ff6b00;">{code}</span>
              </div>
              <p style="color: #666; font-size: 14px;">Este código expira em 10 minutos.</p>
              <p style="color: #999; font-size: 12px; margin-top: 30px; text-align: center;">Se você não solicitou este código, ignore este e-mail.</p>
            </div>
          </body>
        </html>
        """

        part = MIMEText(html, "html")
        msg.attach(part)

        # Connect and Send
        print(f"[EMAIL] Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, email, msg.as_string())

        print(f"[EMAIL] Sent successfully to {email}")
        return True, "Email enviado com sucesso!"

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {email}: {e}")
        return False, f"Erro ao enviar email: {str(e)}"
