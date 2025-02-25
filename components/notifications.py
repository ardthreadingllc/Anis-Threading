import smtplib
import streamlit as st
import os
from email.message import EmailMessage
from components.combo import get_customer_combos 

# Load secrets from Streamlit's secrets manager
SMTP_SERVER = st.secrets["EMAIL_HOST"]  # Fetch from Streamlit secrets
SMTP_PORT = int(st.secrets["EMAIL_PORT"])  # Convert to int
EMAIL_ADDRESS = st.secrets["EMAIL_USER"]  # Fetch email user
EMAIL_PASSWORD = st.secrets["EMAIL_PASS"]  # Fetch email password


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


def format_combo_table(customer_id):
    """
    Fetches the customer's combos and formats them as an HTML table.

    Args:
        customer_id (int): The ID of the customer.
        booked_combo_id (int, optional): The ID of the combo used for booking. Default is None.

    Returns:
        str: Formatted HTML table of customer's combos.
    """
    combos = get_customer_combos(customer_id)
    if not combos:
        return "No active combos"

    table_html = """
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Combo Name</th>
            <th>Remaining Uses</th>
        </tr>
    """

    for combo in combos:
        table_html += f"""
        <tr>
            <td>{combo["name"]}</td>
            <td>{combo["remaining_uses"]}</td>
        </tr>
        """

    table_html += "</table>"
    return table_html


def send_appointment_confirmation(customer_id, customer_name, customer_email, service, date, booked_combo_id):
    """
    Sends an appointment confirmation email to the customer.

    Args:
        customer_name (str): The customer's name.
        customer_email (str): The customer's email address.
        service (str): The booked service.
        date (str): The appointment date (YYYY-MM-DD).
        remaining_uses (int): The remaining uses in the combo.
    """
    combos = get_customer_combos(customer_id)

    #Apply -1 for remaining uses due to email error (lazy way, need to work in future)
    for combo in combos:
        if combo["id"] == booked_combo_id:
            combo["remaining_uses"] -= 1

    # #Generate Table with updated values
    # combo_table = """
    # <table border = "1" cellpadding = "5" cellspacing = "0">
    #     <tr>
    #         <th>Combo Name</th>
    #         <th>Remaining Uses</th>
    #     </tr>
    # """
    # for combo in combos:
    #     combo_table += f"""
    #     <tr>
    #         <td>{combo["name"]}</td>
    #         <td>{combo["remaining_uses"]}</td>
    #     </tr>
    #     """
    # combo_table += "</table>"

    #get latest combo data
    combo_table = format_combo_table(customer_id)

    placeholders = {
        "CUSTOMER_NAME": customer_name,
        "SERVICE": service,
        "DATE": date,
        "COMBO_TABLE": combo_table #insert the table into the email
    }
    email_body = load_email_template("appointment_confirmation.html", placeholders)
    if email_body:
        send_email("Appointment Confirmation - Ani's Threading & Skincare", customer_email, email_body)


def send_appointment_cancellation(customer_id, customer_name, customer_email, service, date):
    """
    Sends an appointment cancellation email to the customer.

    Args:
        customer_name (str): The customer's name.
        customer_email (str): The customer's email address.
        service (str): The cancelled service.
        date (str): The appointment date (YYYY-MM-DD).
        remaining_uses (int): The restored combo uses.
    """
    #get latest combo data
    combo_table = format_combo_table(customer_id)

    placeholders = {
        "CUSTOMER_NAME": customer_name,
        "SERVICE": service,
        "DATE": date,
        "COMBO_TABLE": combo_table #insert table in to email
    }
    email_body = load_email_template("appointment_cancellation.html", placeholders)
    if email_body:
        send_email("Appointment Cancellation - Ani's Threading & Skincare", customer_email, email_body)
