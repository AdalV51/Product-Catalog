import smtplib
from email.mime.text import MIMEText

from catalog_api.database import database


async def send_email(content):
    msg = MIMEText(content)
    recipients = await get_admin_mails()
    msg["Subject"] = "Daily Product Changes Report"
    msg["From"] = "sender@example.com"
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP("mailhog", 1025) as server:  # Use MailHog's SMTP server
        # No login required for MailHog
        server.send_message(msg)


async def get_admin_mails():
    query = "SELECT email FROM users WHERE is_admin == True"
    result = await database.fetch_all(query)
    return [item[0] for item in result]
