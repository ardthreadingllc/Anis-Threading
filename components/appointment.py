import sqlite3
from components.combo import update_combo_usage, get_customer_combos, get_db_connection
from components.customer import get_customer_by_phone
from components.notifications import send_appointment_confirmation, send_appointment_cancellation

# ============================
# Appointment Management
# ============================

def book_appointment(customer_id, service_id, date, use_combo=False, combo_id=None):
    """Books an appointment for a customer and optionally links it to a combo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure the combo is valid if using it
        if use_combo and combo_id:
            cursor.execute("SELECT remaining_uses FROM combos WHERE id = ? AND remaining_uses > 0", (combo_id,))
            combo = cursor.fetchone()
            if not combo:
                print(f"Error: Combo ID {combo_id} is not valid or has no remaining uses.")
                return False

        # Insert appointment into the database
        cursor.execute(
            "INSERT INTO appointments (customer_id, service_id, date, combo_id) VALUES (?, ?, ?, ?)",
            (customer_id, service_id, date, combo_id if use_combo else None)
        )

        # If using a combo, decrement remaining uses using the **same** connection
        if use_combo and combo_id:
            update_combo_usage(combo_id, conn)  # Pass the same connection

        # Fetch updated remaining uses AFTER updating combo
        remaining_uses = None
        if use_combo and combo_id:
            cursor.execute("SELECT remaining_uses FROM combos WHERE id = ?", (combo_id,))
            updated_combo = cursor.fetchone()
            remaining_uses = updated_combo["remaining_uses"] if updated_combo else None

        # Fetch customer details
        customer = get_customer_by_phone(customer_id)

        conn.commit()

        if customer and customer["Email"]:  # Ensure email exists before sending
            send_appointment_confirmation(
                customer["Name"],
                customer["Email"],
                service_id,
                date,
                remaining_uses
            )

        print(f"Appointment booked for Customer ID {customer_id} on {date} (Service ID {service_id}).")
        return True
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return False
    finally:
        conn.close()


def get_customer_appointments(customer_id):
    """
    Retrieves all appointments for a specific customer.

    Args:
        customer_id (int): The ID of the customer.

    Returns:
        list: List of structured appointments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT a.id, c.name, c.phone, s.name AS service, a.date, a.combo_id
               FROM appointments a
               JOIN customers c ON a.customer_id = c.id
               JOIN services s ON a.service_id = s.id
               WHERE a.customer_id = ? 
               ORDER BY a.date""",
            (customer_id,)
        )
        appointments = cursor.fetchall()
        return [
            {"ID": appt["id"], "Name": appt["name"], "Phone": appt["phone"],
             "Service": appt["service"], "Date": appt["date"], "Combo ID": appt["combo_id"]}
            for appt in appointments
        ]
    except Exception as e:
        print(f"Error retrieving appointments: {e}")
        return []
    finally:
        conn.close()

def get_appointment_by_date(date):
    """
    Retrieves all appointments on a specific date.

    Args:
        date (str): The date in 'YYYY-MM-DD' format.

    Returns:
        list: List of structured appointments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT a.id, c.name, c.phone, s.name AS service, a.date, a.combo_id
               FROM appointments a
               JOIN customers c ON a.customer_id = c.id
               JOIN services s ON a.service_id = s.id
               WHERE a.date = ?
               ORDER BY a.date""",
            (date,)
        )
        appointments = cursor.fetchall()
        return [
            {"ID": appt["id"], "Name": appt["name"], "Phone": appt["phone"],
             "Service": appt["service"], "Date": appt["date"], "Combo ID": appt["combo_id"]}
            for appt in appointments
        ]
    except Exception as e:
        print(f"Error retrieving appointments by date: {e}")
        return []
    finally:
        conn.close()

def delete_appointment(appointment_id):
    """Deletes an appointment by its ID, restores combo usage if applicable, and sends a cancellation email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve combo_id, customer_id, service name, and appointment date before deleting the appointment
        cursor.execute("""
            SELECT a.customer_id, c.name, c.email, s.name AS service, a.date, a.combo_id 
            FROM appointments a
            JOIN customers c ON a.customer_id = c.id
            JOIN services s ON a.service_id = s.id
            WHERE a.id = ?
        """, (appointment_id,)
        )

        result = cursor.fetchone()

        if not result:
            print(f"Error: Appointment ID {appointment_id} not found.")
            return False

        combo_id = result["combo_id"]
        customer_id = result["customer_id"]
        customer_name = result["name"]
        customer_email = result["email"]
        service = result["service"]
        date = result["date"]

        print(f"Debug: Attempting to Delete Combo ID {appointment_id}")

        # Delete the appointment
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        if cursor.rowcount == 0:
            print(f"Error: Failed to Delte Appointment {appointment_id}")
            return False
        conn.commit()

        print(f"Debug: Appointment ID {appointment_id} deleted successfully")

        # Restore combo usage if applicable
        remaining_uses = None
        if combo_id:
            cursor.execute("UPDATE combos SET remaining_uses = remaining_uses + 1 WHERE id = ?", (combo_id,))
            conn.commit()

            # Fetch updated remaining uses
            cursor.execute("SELECT remaining_uses FROM combos WHERE id = ?", (combo_id,))
            updated_combo = cursor.fetchone()
            remaining_uses = updated_combo["remaining_uses"] if updated_combo else None

        # Send cancellation email AFTER appointment deletion
        if customer_email and combo_id:
            send_appointment_cancellation(
                customer_name=customer_name,
                customer_email=customer_email,
                service=service,
                date=date,
                remaining_uses=remaining_uses
            )

        return True
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        return False
    finally:
        conn.close()


#function not used as of now, considered for future development
def edit_appointment(appointment_id, new_date, new_service_id):
    """
    Updates the date and service of an appointment.

    Args:
        appointment_id (int): The ID of the appointment to update.
        new_date (str): The new date for the appointment in 'YYYY-MM-DD' format.
        new_service_id (int): The new service ID for the appointment.

    Returns:
        bool: True if successfully updated, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update the appointment
        cursor.execute(
            "UPDATE appointments SET date = ?, service_id = ? WHERE id = ?",
            (new_date, new_service_id, appointment_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} updated to new date {new_date} and service ID {new_service_id}.")
            return True
        else:
            print(f"No appointment found with ID {appointment_id}.")
            return False
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()
