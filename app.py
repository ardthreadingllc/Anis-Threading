import datetime
import streamlit as st
from components.customer import (
    add_customer, get_customer_by_phone, get_all_customers, remove_customer_if_combos_used_up,
    edit_customer, delete_customer
)
from components.combo import (
    add_combo_type, get_combo_types, delete_combo_type, get_customer_combos, add_combo, get_services_for_combo
)
from components.appointment import (
    book_appointment, get_customer_appointments, get_appointment_by_date, delete_appointment, edit_appointment
)
from components.notifications import (
    send_appointment_confirmation, send_appointment_cancellation
)

# Set the title of the app
st.title("Ani's Threading and Skincare Management System")

# Sidebar menu
menu = ["Home", "Customer Management", "Combo Management", "Appointment Management", "View Appointments"]
choice = st.sidebar.selectbox("Menu", menu)

# ============================
# Home Page
# ============================
if choice == "Home":
    st.subheader("Welcome to Ani's Threading and Skincare Management System!")
    st.write("""
        This system allows you to:
        - Manage customers and assign combos.
        - Handle combo packages for discounted services.
        - Schedule and manage appointments.
        - Track combo usage and appointment history.
    """)

# ============================
# Customer Management
# ============================
elif choice == "Customer Management":
    st.subheader("Customer Management")

    # Add a new customer with a combo
    st.write("### Add a New Customer with Combo")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")

    # Dropdown to select a combo type
    combo_types = get_combo_types()
    if combo_types:
        combo_type_options = {f"{combo['name']} (Uses: {combo['total_uses']})": combo['id'] for combo in combo_types}
        selected_combo = st.selectbox("Select a Combo", options=list(combo_type_options.keys()))
        selected_combo_id = combo_type_options[selected_combo]
    else:
        st.warning("No combo types available. Please add combos in the Combo Management tab.")
        selected_combo_id = None

    if st.button("Add Customer with Combo"):
        if selected_combo_id and add_customer(name, phone, email, selected_combo_id):
            st.success(f"Customer '{name}' added successfully with combo '{selected_combo}'!")
            st.session_state["search_query"] = phone  # Auto-store newly added customer for quick lookup
            st.rerun()
        else:
            st.error("Failed to add the customer. Please ensure the information is correct.")

    # Search for a customer by phone
    st.write("### Search Customer by Phone")

    # Ensure search query persists in session state
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

    search_query = st.text_input("Enter Customer Phone Number", st.session_state["search_query"])

    if st.button("Search"):
        customer = get_customer_by_phone(search_query)
        if customer:
            st.session_state["search_query"] = search_query  # Persist search query
            st.session_state["customer_data"] = customer  # Store customer data
            st.session_state["editing"] = False  # Ensure editing state resets
        else:
            st.error("Customer not found.")

    # Display customer details if found
    if "customer_data" in st.session_state and st.session_state["customer_data"]:
        customer = st.session_state["customer_data"]

        st.write("### Customer Details")
        st.write(f"**ID:** {customer['ID']}")
        st.write(f"**Name:** {customer['Name']}")
        st.write(f"**Phone:** {customer['Phone']} (Phone Number is not editable)")
        st.write(f"**Email:** {customer['Email']}")
        st.write(f"**Combos:** {customer['Combos']}")

        # Edit Customer Button
        with st.expander("Edit Customer"):
            new_name = st.text_input("New Name", customer['Name'])
            new_email = st.text_input("New Email", customer['Email'])
            new_remaining_uses = st.number_input("Remaining Uses", min_value=0, value=customer['Combos'][0]["remaining_uses"])

            if st.button("Update Customer Details"):
                result = edit_customer(customer['ID'], new_name, new_email, new_remaining_uses)

                if result == 'email_exists':
                    st.error(f"Failed to update customer. Email '{new_email}' is already in use by another customer.")
                elif result:
                    st.success(f"Customer {customer['Name']} updated successfully!")
                    st.session_state["customer_data"]["Name"] = new_name  # Update session data
                    st.session_state["customer_data"]["Email"] = new_email
                    st.session_state["customer_data"]["Combos"][0]["remaining_uses"] = new_remaining_uses  # Update session
                    st.rerun()
                else:
                    st.error("Failed to update customer.")

        # Delete Customer Button (No Confirmation, Immediate Deletion)
        if st.button("Delete Customer"):
            delete_status = delete_customer(customer['ID'])  # Try deleting the customer
            if delete_status:
                st.success(f"Customer {customer['Name']} deleted successfully!")
                
                # Ensure UI refreshes correctly
                st.session_state.pop("customer_data", None)
                st.session_state.pop("search_query", None)
                st.rerun()
            else:
                st.error("Failed to delete customer. Customer might not exist.")


    # Show all customers on button click
    if st.button("Show All Customers"):
        st.write("### All Customers")
        customers = get_all_customers()
        if customers:
            for customer in customers:
                st.write(f"**ID:** {customer['ID']}")
                st.write(f"**Name:** {customer['Name']}")
                st.write(f"**Phone:** {customer['Phone']}")
                st.write(f"**Email:** {customer['Email']}")
                st.write(f"**Combos:** {customer['Combos']}")
                st.write("---")
        else:
            st.write("No customers found.")

# ============================
# Combo Management
# ============================
elif choice == "Combo Management":
    st.subheader("Combo Management")

    # Add a new combo type
    st.write("### Add a New Combo Type")
    combo_name = st.text_input("Combo Name")
    total_uses = st.number_input("Total Uses", min_value=1, step=1)

    all_services = get_services_for_combo(None)
    service_options = {service['name']: service['id'] for service in all_services}
    selected_services = st.multiselect("Select Services for Combo", list(service_options.keys()))

    if st.button("Add Combo Type"):
        selected_service_ids = [service_options[service] for service in selected_services]
        if add_combo_type(combo_name, selected_service_ids, total_uses):
            st.success(f"Combo type '{combo_name}' added successfully with services {selected_services}!")
            st.rerun()
        else:
            st.error("Failed to add the combo type. It may already exist.")

    # View, edit, and delete combo types
    st.write("### Existing Combo Types")
    combo_types = get_combo_types()
    if combo_types:
        for combo in combo_types:
            st.write(f"**ID:** {combo['id']}, **Name:** {combo['name']}, **Total Uses:** {combo['total_uses']}")
            if st.button(f"Delete Combo '{combo['name']}'", key=f"delete_combo_{combo['id']}"):
                if delete_combo_type(combo['id']):
                    st.success(f"Combo '{combo['name']}' deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to delete combo '{combo['name']}'.")

# ============================
# Appointment Management
# ============================
elif choice == "Appointment Management":
    st.subheader("Appointment Management")

    st.write("### Book an Appointment")
    phone = st.text_input("Customer Phone Number (for appointment)")
    date = st.date_input("Appointment Date")

    customer = get_customer_by_phone(phone) if phone else None

    if customer:
        all_services = get_services_for_combo(None)
        service_options = {service['name']: service['id'] for service in all_services}
        selected_service = st.selectbox("Select a Service", list(service_options.keys()))
        selected_service_id = service_options[selected_service]

        use_combo = st.checkbox("Use Available Combo")
        selected_combo_id = None

        if use_combo:
            available_combos = get_customer_combos(customer["ID"])
            if available_combos:
                combo_options = {f"{combo['name']} (Remaining: {combo['remaining_uses']})": combo['id'] for combo in available_combos}
                selected_combo = st.selectbox("Select a Combo", options=list(combo_options.keys()))
                selected_combo_id = combo_options[selected_combo]
            else:
                st.warning("No available combos for this customer.")

        if st.button("Book Appointment"):
            if book_appointment(customer["ID"], selected_service_id, str(date), use_combo=True, combo_id=selected_combo_id):
                st.success(f"Appointment booked for {customer['Name']} on {date} with service {selected_service}!")
                
                # Send email confirmation if customer has an email
                if customer["Email"]:
                    send_appointment_confirmation(
                        customer["Name"], customer["Email"], selected_service, date,
                        next(combo["remaining_uses"] for combo in customer["Combos"] if combo["id"] == selected_combo_id)
                        if selected_combo_id else None
                    )
                
                st.rerun()
            else:
                st.error("Failed to book appointment.")

# ============================
# View Appointments
# ============================
elif choice == "View Appointments":
    st.subheader("View Appointments")

    # Ensure selected date exists and is valid
    if "selected_date" not in st.session_state or not isinstance(st.session_state["selected_date"], datetime.date):
        st.session_state["selected_date"] = datetime.date.today()  # Default to today

    # Properly set date_to_check
    date_to_check = st.date_input("Select a Date", value=st.session_state["selected_date"])

    if st.button("View Appointments by Date"):
        st.session_state["selected_date"] = date_to_check  # Store selected date
        appointments = get_appointment_by_date(str(st.session_state["selected_date"]))
        st.session_state["appointments"] = appointments  # Store appointments in session
        st.rerun()  # Refresh UI

    # Display appointments
    if "appointments" in st.session_state and st.session_state["appointments"]:
        for appointment in st.session_state["appointments"]:
            st.write(f"**Appointment ID:** {appointment['ID']}")
            st.write(f"**Customer:** {appointment['Name']} ({appointment['Phone']})")
            st.write(f"**Service:** {appointment['Service']}")
            st.write(f"**Date:** {appointment['Date']}")

            # Delete appointment button
            if st.button(f"Delete Appointment {appointment['ID']}", key=f"delete_appointment_{appointment['ID']}"):
                if delete_appointment(appointment['ID']):
                    st.success(f"Appointment ID {appointment['ID']} deleted successfully!")

                    # Remove deleted appointment from session manually
                    st.session_state["appointments"] = [
                        appt for appt in st.session_state["appointments"] if appt["ID"] != appointment["ID"]
                    ]
                    st.rerun()
                else:
                    st.error(f"Failed to Delete the appointment ID {appointment["ID"]}")
            st.write("---") #seperator
    else:
        st.write("No appointments found on this date")