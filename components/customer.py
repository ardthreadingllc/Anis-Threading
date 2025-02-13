import sqlite3
from components.combo import add_combo, get_customer_combos, get_db_connection

# ============================
# Customer Management
# ============================

def add_customer(name, phone, combo_type_id):
    """Adds a new customer and assigns an initial combo to them."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Add customer to the database
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        customer_id = cursor.lastrowid  # Get the new customer ID

        print(f"Debug: Customer '{name}' added with ID {customer_id}")

        # Assign the initial combo
        if not add_combo(customer_id, combo_type_id, conn):
            raise Exception("Failed to add combo for the customer.")

        conn.commit()
        print(f"Customer '{name}' added successfully with combo type ID {combo_type_id}!")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Customer with phone number '{phone}' already exists.")
        return False
    except Exception as e:
        print(f"Error adding customer: {e}")
        return False
    finally:
        conn.close()

def get_customer_by_phone(phone):
    """Retrieves a customer's information using their phone number only."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        customer = cursor.fetchone()
        
        if not customer:
            print(f"Debug: No customer found for phone number '{phone}'")
            return None  # No customer found

        customer_id = customer["id"]
        customer_combos = get_customer_combos(customer_id)

        print(f"Debug: Retrieved Customer {customer_id}: {customer}")
        print(f"Debug: Customer {customer_id} Combos: {customer_combos}")

        return {
            "ID": customer_id,
            "Name": customer["name"],
            "Phone": customer["phone"],
            "Combos": customer_combos  # List of active combos
        }
    except Exception as e:
        print(f"Error retrieving customer: {e}")
        return None
    finally:
        conn.close()

def get_all_customers():
    """Retrieves all customers and their assigned combos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()

        print(f"Debug: Retrieved Customers from DB: {customers}")

        customer_list = []
        for customer in customers:
            customer_id = customer["id"]
            customer_combos = get_customer_combos(customer_id)

            customer_list.append({
                "ID": customer_id,
                "Name": customer["name"],
                "Phone": customer["phone"],
                "Combos": customer_combos
            })

        return customer_list
    except Exception as e:
        print(f"Error retrieving customers: {e}")
        return []
    finally:
        conn.close()

def edit_customer(customer_id, new_name, new_phone):
    """Edits a customer's name and phone number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE customers SET name = ?, phone = ? WHERE id = ?",
            (new_name, new_phone, customer_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            print(f"Error: Customer ID {customer_id} not found or no changes made.")
            return False

        print(f"Customer ID {customer_id} updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating customer: {e}")
        return False
    finally:
        conn.close()

def delete_customer(customer_id):
    """Deletes a customer ONLY if they have no active combos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the customer has active combos
        cursor.execute("SELECT COUNT(*) FROM combos WHERE customer_id = ? AND remaining_uses > 0", (customer_id,))
        active_combos = cursor.fetchone()[0]

        if active_combos > 0:
            print(f"Error: Cannot delete customer ID {customer_id} because they have active combos.")
            return False

        # Delete the customer
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        print(f"Customer ID {customer_id} deleted successfully!")
        return True
    except Exception as e:
        print(f"Error deleting customer: {e}")
        return False
    finally:
        conn.close()

def remove_customer_if_combos_used_up(customer_id):
    """Checks if a customer has any remaining combos and deletes them if all combos are used up."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM combos WHERE customer_id = ? AND remaining_uses > 0",
            (customer_id,)
        )
        active_combos_count = cursor.fetchone()[0]
        if active_combos_count == 0:
            return delete_customer(customer_id)  # Now this checks for active combos before deletion
        return False
    except Exception as e:
        print(f"Error checking customer combos: {e}")
        return False
    finally:
        conn.close()
