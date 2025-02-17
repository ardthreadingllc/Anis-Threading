from components.notifications import send_appointment_confirmation, send_appointment_cancellation

# Test Customer Details
test_customer_name = "Sai Praneeth"
test_customer_email = "bvspr489@gmail.com"  # Change this to your own email for testing
test_service = "Eyebrow Threading"
test_date = "2025-02-15"
test_remaining_uses = 3

# Test Appointment Confirmation Email
print("Testing appointment confirmation email...")
send_appointment_confirmation(test_customer_name, test_customer_email, test_service, test_date, test_remaining_uses)

# Test Appointment Cancellation Email
print("Testing appointment cancellation email...")
send_appointment_cancellation(test_customer_name, test_customer_email, test_service, test_date, test_remaining_uses)
