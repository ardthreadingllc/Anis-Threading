import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

# ============================
# Helper Function
# ============================

def get_db_connection():
    """Provides a single database connection with timeout."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row  # Makes query results more readable
    return conn

# ============================
# Combo Types Management
# ============================

def add_combo_type(name, services, total_uses):
    """Adds a new combo type and associates it with selected services."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the combo already exists
        cursor.execute("SELECT id FROM combo_types WHERE name = ?", (name,))
        existing_combo = cursor.fetchone()
        if existing_combo:
            print(f"Error: Combo type '{name}' already exists.")
            return False

        # Insert the combo type
        cursor.execute(
            "INSERT INTO combo_types (name, total_uses) VALUES (?, ?)",
            (name, total_uses)
        )
        combo_type_id = cursor.lastrowid

        # Insert the services linked to the combo
        for service_id in services:
            cursor.execute(
                "INSERT INTO combo_services (combo_type_id, service_id) VALUES (?, ?)",
                (combo_type_id, service_id)
            )

        conn.commit()
        print(f"Combo type '{name}' added successfully!")
        return True
    except Exception as e:
        print(f"Error adding combo type: {e}")
        return False
    finally:
        conn.close()

def get_combo_types():
    """Retrieves all available combo types."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM combo_types")
        combo_types = cursor.fetchall()

        return [
            {"id": combo["id"], "name": combo["name"], "total_uses": combo["total_uses"]}
            for combo in combo_types
        ]
    except Exception as e:
        print(f"Error retrieving combo types: {e}")
        return []
    finally:
        conn.close()

def get_services_for_combo(combo_type_id=None):
    """Retrieves all services or services linked to a specific combo type."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if combo_type_id:
            cursor.execute(
                """SELECT s.id, s.name FROM services s
                   JOIN combo_services cs ON s.id = cs.service_id
                   WHERE cs.combo_type_id = ?""",
                (combo_type_id,)
            )
        else:
            cursor.execute("SELECT id, name FROM services")
        
        services = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
        return services
    except Exception as e:
        print(f"Error retrieving services for combo: {e}")
        return []
    finally:
        conn.close()
        
def delete_combo_type(combo_type_id):
    """Deletes a combo type from the system, including its service mappings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete services mapped to this combo
        cursor.execute("DELETE FROM combo_services WHERE combo_type_id = ?", (combo_type_id,))

        # Delete the combo type
        cursor.execute("DELETE FROM combo_types WHERE id = ?", (combo_type_id,))
        conn.commit()
        print(f"Combo type ID {combo_type_id} deleted successfully!")
        return True
    except Exception as e:
        print(f"Error deleting combo type: {e}")
        return False
    finally:
        conn.close()

# ============================
# Customer Combo Management
# ============================

def add_combo(customer_id, combo_type_id, conn=None):
    """Assigns a combo to a customer using a shared connection if provided."""
    should_close_connection = False
    if conn is None:
        conn = get_db_connection()
        should_close_connection = True

    cursor = conn.cursor()
    try:
        # Retrieve total uses from the combo_types table
        cursor.execute("SELECT total_uses FROM combo_types WHERE id = ?", (combo_type_id,))
        result = cursor.fetchone()
        if not result:
            print(f"Error: Combo type ID {combo_type_id} does not exist.")
            return False
        total_uses = result["total_uses"]

        # Add combo to the combos table
        cursor.execute(
            "INSERT INTO combos (customer_id, combo_type_id, remaining_uses) VALUES (?, ?, ?)",
            (customer_id, combo_type_id, total_uses)
        )
        conn.commit()
        print(f"Combo for customer ID {customer_id} added successfully!")
        return True
    except Exception as e:
        print(f"Error adding combo: {e}")
        return False
    finally:
        if should_close_connection:
            conn.close()

def get_customer_combos(customer_id):
    """Retrieves all active combos for a specific customer (remaining uses > 0)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.id, ct.name, c.remaining_uses, ct.total_uses
            FROM combos c
            JOIN combo_types ct ON c.combo_type_id = ct.id
            WHERE c.customer_id = ? AND c.remaining_uses > 0
        """, (customer_id,))
        
        combos = cursor.fetchall()
        return [
            {"id": combo["id"], "name": combo["name"], "remaining_uses": combo["remaining_uses"], "total_uses": combo["total_uses"]}
            for combo in combos
        ]
    except Exception as e:
        print(f"Error retrieving customer combos: {e}")
        return []
    finally:
        conn.close()

def update_combo_usage(combo_id, conn=None):
    """Decreases the remaining uses of a combo by 1."""
    should_close_connection = False
    if conn is None:
        conn = get_db_connection()
        should_close_connection = True

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE combos SET remaining_uses = remaining_uses - 1 WHERE id = ? AND remaining_uses > 0",
            (combo_id,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Debug: Combo ID {combo_id} usage updated successfully!")
            return True
        else:
            print(f"Error: Combo ID {combo_id} has no remaining uses or does not exist.")
            return False
    except Exception as e:
        print(f"Error updating combo usage: {e}")
        return False
    finally:
        if should_close_connection:
            conn.close()
