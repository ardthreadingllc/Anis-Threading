import smtplib
import os
from email.message import EmailMessage

EMAIL_ADDRESS = os.getenv("GMAIL_SMTP_PASS")
EMAIL_PASSWORD = os.getenv("OUTLOOK_SMTP_PASS")

email = EmailMessage()
email['from'] = "Ani's Threading and Skincare"
email['to'] = "bvspr489@gmail.com"
email['subject'] = "Test Email from Anis smtp"

email.set_content("This is a test email.")

with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login("anisthreadingnskincare@gmail.com", EMAIL_PASSWORD)
    smtp.send_message(email)
    print("all good mate!")