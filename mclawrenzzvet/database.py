import sqlite3
from datetime import datetime
import tkinter.messagebox as messagebox
from config import DB_FILE

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)

def init_db():
    """Initialize database with all required tables"""
    try:
        conn = get_db()
        cur = conn.cursor()

        # Users table - Enhanced with more roles
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'staff'
            )
            """
        )

        # Check if role column exists, if not add it
        try:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'staff'")
        except sqlite3.Error:
            pass  # Column already exists

        # Inventory table
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'"
        )
        inv_exists = cur.fetchone()

        if not inv_exists:
            cur.execute(
                """
                CREATE TABLE inventory(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL,
                    stock INTEGER,
                    category TEXT,
                    image TEXT,
                    brand TEXT,
                    animal_type TEXT,
                    dosage TEXT,
                    expiration_date TEXT
                )
                """
            )
        else:
            cur.execute("PRAGMA table_info(inventory)")
            cols = {row[1] for row in cur.fetchall()}
            extra_cols = {
                "brand": "ALTER TABLE inventory ADD COLUMN brand TEXT",
                "animal_type": "ALTER TABLE inventory ADD COLUMN animal_type TEXT",
                "dosage": "ALTER TABLE inventory ADD COLUMN dosage TEXT",
                "expiration_date": "ALTER TABLE inventory ADD COLUMN expiration_date TEXT",
            }
            for col, sql in extra_cols.items():
                if col not in cols:
                    try:
                        cur.execute(sql)
                    except sqlite3.Error:
                        pass  # Column might already exist

        # Drop and recreate appointments table to ensure correct structure
        cur.execute("DROP TABLE IF EXISTS appointments")
        cur.execute(
            """
            CREATE TABLE appointments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT,
                patient_name TEXT,
                owner_name TEXT,
                animal_type TEXT,
                service TEXT,
                qty INTEGER,
                price REAL,
                subtotal REAL,
                date TEXT,
                notes TEXT,
                status TEXT,
                total_amount REAL
            )
            """
        )

        # Enhanced appointments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments_enhanced(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT,
                patient_name TEXT,
                owner_name TEXT,
                animal_type TEXT,
                service TEXT,
                veterinarian TEXT,
                duration INTEGER,
                appointment_date TEXT,
                appointment_time TEXT,
                date_created TEXT,
                notes TEXT,
                status TEXT,
                total_amount REAL,
                reminder_sent BOOLEAN DEFAULT 0,
                follow_up_needed BOOLEAN DEFAULT 0
            )
        """)

        # Appointment services table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment_services(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT,
                service_name TEXT,
                quantity INTEGER,
                price REAL,
                subtotal REAL
            )
        """)

        # Communication log table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS communication_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT,
                communication_type TEXT,
                sent_to TEXT,
                message TEXT,
                sent_date TEXT,
                status TEXT
            )
        """)

        # Sales table
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sales'"
        )
        sales_exists = cur.fetchone()

        if not sales_exists:
            cur.execute(
                """
                CREATE TABLE sales(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    item_id INTEGER,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    subtotal REAL,
                    total_amount REAL,
                    payment_method TEXT,
                    customer_name TEXT,
                    sale_date TEXT
                )
                """
            )

        # Insert default users with different roles
        default_users = [
            ("admin", "admin123", "admin"),
            ("staff", "staff123", "staff"),
            ("vet_smith", "vet123", "veterinarian"),
            ("reception", "recep123", "receptionist")
        ]
        
        for username, password, role in default_users:
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO users (username, password, role)
                    VALUES (?, ?, ?)
                    """,
                    (username, password, role),
                )

        conn.commit()
        conn.close()
        
        # Clear any existing test data
        clear_test_data()
        
        print("Database initialized successfully!")
        return True

    except sqlite3.Error as e:
        print(f"Database initialization error: {str(e)}")
        messagebox.showerror(
            "Database Error", f"Database initialization failed: {str(e)}")
        return False

def clear_test_data():
    """Clear any test appointment data that might exist"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Check if there are any appointments and delete them
        cur.execute("SELECT COUNT(*) FROM appointments")
        count = cur.fetchone()[0]
        
        if count > 0:
            cur.execute("DELETE FROM appointments")
            conn.commit()
            print(f"Cleared {count} test appointments from database")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Error clearing test data: {e}")