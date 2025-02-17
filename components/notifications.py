import smtplib
import os
from email.message import EmailMessage

# Load environment variables for Gmail SMTP authentication
SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
SMTP_PORT = 587  # TLS port
EMAIL_ADDRESS = "anisthreadingnskincare@gmail.com"  # Sender email
EMAIL_PASSWORD = "sgrq nurt bnli fbun"  # App password


def load_email_template(template_name, placeholders):
    """
    Loads an email template and replaces placeholders with actual values.

    Args:
        template_name (str): The name of the email template file.
        placeholders (dict): A dictionary of placeholder keys and values.

    Returns:
        str: The formatted email content.
    """
    template_path = os.path.join("templates", template_name)
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
        for key, value in placeholders.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template
    except FileNotFoundError:
        print(f"Error: Email template '{template_name}' not found.")
        return None


def send_email(subject, to_email, email_body):
    """
    Sends an email using the configured SMTP server.

    Args:
        subject (str): The email subject.
        to_email (str): The recipient's email address.
        email_body (str): The email body (HTML format).

    Returns:
        bool: True if email is sent successfully, False otherwise.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Error: Email credentials not set in environment variables.")
        return False

    try:
        # Construct the email
        email = EmailMessage()
        email["From"] = EMAIL_ADDRESS
        email["To"] = to_email
        email["Subject"] = subject
        email.set_content(email_body, subtype="html")  # Send HTML email

        # Connect to Gmail SMTP Server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.ehlo()  # Identify ourselves to the SMTP server
            smtp.starttls()  # Secure the connection
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in
            smtp.send_message(email)  # Send the email

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_appointment_confirmation(customer_name, customer_email, service, date, remaining_uses):
    """
    Sends an appointment confirmation email to the customer.

    Args:
        customer_name (str): The customer's name.
        customer_email (str): The customer's email address.
        service (str): The booked service.
        date (str): The appointment date (YYYY-MM-DD).
        remaining_uses (int): The remaining uses in the combo.
    """
    placeholders = {
        "CUSTOMER_NAME": customer_name,
        "SERVICE": service,
        "DATE": date,
        "REMAINING_USES": remaining_uses
    }
    email_body = load_email_template("appointment_confirmation.html", placeholders)
    if email_body:
        send_email("Appointment Confirmation - Ani's Threading & Skincare", customer_email, email_body)


def send_appointment_cancellation(customer_name, customer_email, service, date, remaining_uses):
    """
    Sends an appointment cancellation email to the customer.

    Args:
        customer_name (str): The customer's name.
        customer_email (str): The customer's email address.
        service (str): The cancelled service.
        date (str): The appointment date (YYYY-MM-DD).
        remaining_uses (int): The restored combo uses.
    """
    placeholders = {
        "CUSTOMER_NAME": customer_name,
        "SERVICE": service,
        "DATE": date,
        "REMAINING_USES": remaining_uses
    }
    email_body = load_email_template("appointment_cancellation.html", placeholders)
    if email_body:
        send_email("Appointment Cancellation - Ani's Threading & Skincare", customer_email, email_body)
