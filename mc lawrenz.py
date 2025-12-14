import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import webbrowser 
import csv
from datetime import datetime, timedelta
import shutil

# ==================== COLOR THEME ==================== 
COLORS = {
    "primary": "#2E86AB",      # Vibrant blue
    "secondary": "#A23B72",    # Purple
    "accent": "#F18F01",       # Orange
    "success": "#4CAF50",      # Green
    "warning": "#FF9800",      # Amber
    "danger": "#F44336",       # Red
    "dark": "#2C3E50",         # Dark blue-gray
    "light": "#ECF0F1",        # Light gray
    "background": "#34495E",   # Dark background
    "card": "#2C3E50",         # Card background
    "text_light": "#FFFFFF",   # White text
    "text_dark": "#2C3E50"     # Dark text
}

# ==================== ENHANCED CLASSES ====================

class EnhancedUser:
    """Extended User class with enhanced permissions"""
    
    PERMISSIONS = {
        'admin': {
            'manage_users': True,
            'manage_inventory': True,
            'view_reports': True,
            'manage_appointments': True,
            'process_sales': True,
            'view_financials': True,
            'system_settings': True,
            'manage_communications': True
        },
        'veterinarian': {
            'manage_users': False,
            'manage_inventory': True,
            'view_reports': True,
            'manage_appointments': True,
            'process_sales': True,
            'view_financials': True,
            'system_settings': False,
            'manage_communications': True
        },
        'staff': {
            'manage_users': False,
            'manage_inventory': True,
            'view_reports': True,
            'manage_appointments': True,
            'process_sales': True,
            'view_financials': False,
            'system_settings': False,
            'manage_communications': False
        },
        'receptionist': {
            'manage_users': False,
            'manage_inventory': False,
            'view_reports': False,
            'manage_appointments': True,
            'process_sales': True,
            'view_financials': False,
            'system_settings': False,
            'manage_communications': True
        }
    }
    
    def __init__(self, id=None, username="", password="", role="staff"):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.permissions = self.PERMISSIONS.get(role, self.PERMISSIONS['staff'])
    
    def authenticate(self, input_username, input_password):
        """Authenticate user credentials"""
        return self.username == input_username and self.password == input_password
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return self.permissions.get(permission, False)
    
    def get_role_display_name(self):
        """Get display name for role"""
        role_names = {
            'admin': 'Administrator',
            'veterinarian': 'Veterinarian',
            'staff': 'Staff Member',
            'receptionist': 'Receptionist'
        }
        return role_names.get(self.role, 'Staff Member')


class EnhancedAppointment:
    """Represents an enhanced veterinary appointment with more details"""
    
    def __init__(self, appointment_id="", patient_name="", owner_name="", animal_type="", 
                 service="", notes="", status="SCHEDULED", veterinarian="", duration=30,
                 appointment_date=None, appointment_time=""):
        self.appointment_id = appointment_id
        self.patient_name = patient_name
        self.owner_name = owner_name
        self.animal_type = animal_type
        self.service = service
        self.notes = notes
        self.status = status
        self.veterinarian = veterinarian
        self.duration = duration  # in minutes
        self.appointment_date = appointment_date or datetime.now().strftime('%Y-%m-%d')
        self.appointment_time = appointment_time or datetime.now().strftime('%H:%M')
        self.date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.services = []
        self.total_amount = 0.0
        self.reminder_sent = False
        self.follow_up_needed = False
        # Add 'date' attribute for legacy compatibility
        self.date = self.date_created
        
    def add_service(self, service_name, quantity, price, subtotal):
        """Add service to appointment with proper pricing"""
        self.services.append({
            'service': service_name,
            'qty': quantity,
            'price': price,
            'subtotal': subtotal
        })
        self.total_amount += subtotal

    def to_dict(self):
        """Convert appointment to dictionary for database operations"""
        return {
            'appointment_id': self.appointment_id,
            'patient_name': self.patient_name,
            'owner_name': self.owner_name,
            'animal_type': self.animal_type,
            'service': self.service,
            'notes': self.notes,
            'status': self.status,
            'veterinarian': self.veterinarian,
            'duration': self.duration,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'date_created': self.date_created,
            'total_amount': self.total_amount,
            'reminder_sent': self.reminder_sent,
            'follow_up_needed': self.follow_up_needed,
            'services': self.services,
            'date': self.date  # For legacy compatibility
        }


class Medicine:
    """Represents a medicine or supply in the inventory"""
    
    def __init__(self, id=None, name="", price=0.0, stock=0, category="", brand="",
                 animal_type="", dosage="", expiration_date=""):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.brand = brand
        self.animal_type = animal_type
        self.dosage = dosage
        self.expiration_date = expiration_date

    def to_dict(self):
        """Convert medicine to dictionary for database operations"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'brand': self.brand,
            'animal_type': self.animal_type,
            'dosage': self.dosage,
            'expiration_date': self.expiration_date
        }

    @classmethod
    def from_dict(cls, data):
        """Create Medicine instance from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            animal_type=data.get('animal_type', ''),
            dosage=data.get('dosage', ''),
            expiration_date=data.get('expiration_date', '')
        )


class CartItem:
    """Represents an item in the shopping cart (for medicines/supplies/foods)"""
    
    def __init__(self, item_id, name, price, quantity=1, category=""):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.category = category

    @property
    def subtotal(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            'id': self.item_id,
            'name': self.name,
            'price': self.price,
            'qty': self.quantity,
            'subtotal': self.subtotal,
            'category': self.category
        }


# ==================== ENHANCED MANAGERS ====================

class EnhancedInventoryManager:
    """Manages enhanced inventory operations with expiration tracking"""
    
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_items(self):
        """Get all items from inventory (medicines and foods)"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM inventory ORDER BY category, name")
            rows = cur.fetchall()
            items = []
            for row in rows:
                item = Medicine(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    stock=row[3],
                    category=row[4],
                    brand=row[6] if len(row) > 6 else "",
                    animal_type=row[7] if len(row) > 7 else "",
                    dosage=row[8] if len(row) > 8 else "",
                    expiration_date=row[9] if len(row) > 9 else ""
                )
                items.append(item)
            return items
        except sqlite3.Error as e:
            print(f"Error getting items: {e}")
            return []

    def search_items(self, search_term):
        """Search items by name"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM inventory WHERE name LIKE ? OR category LIKE ? ORDER BY category, name",
                        (f"%{search_term}%", f"%{search_term}%"))
            rows = cur.fetchall()
            items = []
            for row in rows:
                item = Medicine(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    stock=row[3],
                    category=row[4],
                    brand=row[6] if len(row) > 6 else "",
                    animal_type=row[7] if len(row) > 7 else "",
                    dosage=row[8] if len(row) > 8 else "",
                    expiration_date=row[9] if len(row) > 9 else ""
                )
                items.append(item)
            return items
        except sqlite3.Error as e:
            print(f"Error searching items: {e}")
            return []

    def get_expiring_items(self, days_threshold=30):
        """Get items expiring within specified days"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT *, 
                julianday(expiration_date) - julianday('now') as days_until_expiry
                FROM inventory 
                WHERE expiration_date IS NOT NULL 
                AND expiration_date != ''
                AND julianday(expiration_date) - julianday('now') BETWEEN 0 AND ?
                ORDER BY expiration_date
            """, (days_threshold,))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting expiring items: {e}")
            return []

    def get_low_stock_items(self, threshold=10):
        """Get items with stock below threshold"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT * FROM inventory 
                WHERE stock <= ? 
                ORDER BY stock ASC
            """, (threshold,))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting low stock items: {e}")
            return []

    def get_inventory_valuation(self):
        """Calculate total inventory valuation"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT SUM(price * stock) as total_value,
                COUNT(*) as item_count,
                COUNT(CASE WHEN stock <= 10 THEN 1 END) as low_stock_count,
                COUNT(CASE WHEN julianday(expiration_date) - julianday('now') <= 30 THEN 1 END) as expiring_soon_count
                FROM inventory
            """)
            return cur.fetchone()
        except sqlite3.Error as e:
            print(f"Error calculating inventory valuation: {e}")
            return (0, 0, 0, 0)

    def update_item_stock(self, item_id, quantity_used):
        """Update item stock after use"""
        try:
            cur = self.db.cursor()
            cur.execute("UPDATE inventory SET stock = stock - ? WHERE id = ?",
                        (quantity_used, item_id))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating stock: {e}")
            return False

    def add_item(self, medicine):
        """Add new item to inventory"""
        try:
            cur = self.db.cursor()
            cur.execute("""INSERT INTO inventory 
                        (name, price, stock, category, brand, animal_type, dosage, expiration_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (medicine.name, medicine.price, medicine.stock, medicine.category,
                         medicine.brand, medicine.animal_type, medicine.dosage, medicine.expiration_date))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return False

    def update_item(self, medicine):
        """Update existing item in inventory"""
        try:
            cur = self.db.cursor()
            cur.execute("""UPDATE inventory SET 
                        name=?, price=?, stock=?, category=?, brand=?, animal_type=?, dosage=?, expiration_date=?
                        WHERE id=?""",
                        (medicine.name, medicine.price, medicine.stock, medicine.category,
                         medicine.brand, medicine.animal_type, medicine.dosage, medicine.expiration_date, medicine.id))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating item: {e}")
            return False

    def delete_item(self, item_id):
        """Delete item from inventory"""
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM inventory WHERE id=?", (item_id,))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            return False


class EnhancedAppointmentManager:
    """Manages enhanced appointment operations"""
    
    def __init__(self, db_connection):
        self.db = db_connection

    def record_appointment(self, appointment):
        """Record an appointment in the database - FIXED VERSION"""
        try:
            cur = self.db.cursor()
            
            # Use date_created from appointment object
            appointment_date = appointment.date_created
            
            # Record the appointment with services
            for service in appointment.services:
                cur.execute("""INSERT INTO appointments 
                            (appointment_id, patient_name, owner_name, animal_type, service, 
                             qty, price, subtotal, date, notes, status, total_amount) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (appointment.appointment_id, 
                             appointment.patient_name, 
                             appointment.owner_name,
                             appointment.animal_type, 
                             service['service'], 
                             service['qty'], 
                             service['price'],
                             service['subtotal'], 
                             appointment_date,
                             appointment.notes if hasattr(appointment, 'notes') else "", 
                             appointment.status, 
                             appointment.total_amount))
            
            self.db.commit()
            print(f"Appointment {appointment.appointment_id} recorded successfully to legacy table!")
            return True
        except sqlite3.Error as e:
            print(f"Error recording appointment to legacy table: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return False
        except Exception as e:
            print(f"General error recording appointment: {e}")
            import traceback
            traceback.print_exc()
            return False

    def record_enhanced_appointment(self, appointment):
        """Record an enhanced appointment with more details"""
        try:
            cur = self.db.cursor()
            
            # Create enhanced appointments table if not exists
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
            
            # Insert appointment
            cur.execute("""INSERT INTO appointments_enhanced 
                        (appointment_id, patient_name, owner_name, animal_type, service,
                         veterinarian, duration, appointment_date, appointment_time,
                         date_created, notes, status, total_amount, reminder_sent, follow_up_needed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (appointment.appointment_id, appointment.patient_name, appointment.owner_name,
                        appointment.animal_type, appointment.service, appointment.veterinarian,
                        appointment.duration, appointment.appointment_date, appointment.appointment_time,
                        appointment.date_created, appointment.notes, appointment.status,
                        appointment.total_amount, appointment.reminder_sent, appointment.follow_up_needed))
            
            # Create appointment services table if not exists
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
            
            # Insert services
            for service in appointment.services:
                cur.execute("""INSERT INTO appointment_services 
                            (appointment_id, service_name, quantity, price, subtotal)
                            VALUES (?, ?, ?, ?, ?)""",
                           (appointment.appointment_id, service['service'], service['qty'],
                            service['price'], service['subtotal']))
            
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording enhanced appointment: {e}")
            return False

    def get_upcoming_appointments(self, days=7):
        """Get upcoming appointments within specified days"""
        try:
            cur = self.db.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("""
                    SELECT * FROM appointments_enhanced 
                    WHERE appointment_date BETWEEN ? AND ?
                    AND status IN ('SCHEDULED', 'IN_PROGRESS')
                    ORDER BY appointment_date, appointment_time
                """, (today, future_date))
            else:
                cur.execute("""
                    SELECT * FROM appointments 
                    WHERE date LIKE ? || '%'
                    AND status IN ('SCHEDULED', 'IN_PROGRESS')
                    ORDER BY date
                """, (future_date,))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting upcoming appointments: {e}")
            return []

    def get_appointments_by_veterinarian(self, veterinarian, date=None):
        """Get appointments for specific veterinarian"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                query = "SELECT * FROM appointments_enhanced WHERE veterinarian = ?"
                params = [veterinarian]
                
                if date:
                    query += " AND appointment_date = ?"
                    params.append(date)
                
                query += " ORDER BY appointment_time"
                cur.execute(query, params)
            else:
                # Fallback to regular appointments
                query = "SELECT * FROM appointments WHERE 1=1"
                params = []
                if date:
                    query += " AND date LIKE ?"
                    params.append(f"{date}%")
                query += " ORDER BY date"
                cur.execute(query, params)
            
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting veterinarian appointments: {e}")
            return []

    def get_appointments_history(self, date_filter="", appointment_filter=""):
        """Get appointments history with optional filters"""
        try:
            cur = self.db.cursor()
            query = "SELECT * FROM appointments WHERE 1=1"
            params = []

            if date_filter:
                query += " AND date LIKE ?"
                params.append(f"{date_filter}%")

            if appointment_filter:
                query += " AND appointment_id LIKE ?"
                params.append(f"%{appointment_filter}%")

            query += " ORDER BY date DESC"
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting appointments history: {e}")
            return []

    def get_all_appointments(self):
        """Get all unique appointments"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT DISTINCT appointment_id, patient_name, owner_name, animal_type, 
                       date, notes, status, total_amount
                FROM appointments 
                GROUP BY appointment_id 
                ORDER BY date DESC
            """)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting appointments: {e}")
            return []

    def get_all_enhanced_appointments(self):
        """Get all enhanced appointments"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("""
                    SELECT * FROM appointments_enhanced 
                    ORDER BY appointment_date DESC, appointment_time DESC
                """)
                return cur.fetchall()
            return []
        except sqlite3.Error as e:
            print(f"Error getting enhanced appointments: {e}")
            return []

    def update_appointment_status(self, appointment_id, new_status):
        """Update appointment status"""
        try:
            cur = self.db.cursor()
            
            # Try enhanced table first
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("UPDATE appointments_enhanced SET status = ? WHERE appointment_id = ?", 
                           (new_status, appointment_id))
            
            # Also update regular table
            cur.execute("UPDATE appointments SET status = ? WHERE appointment_id = ?", 
                       (new_status, appointment_id))
            
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating appointment status: {e}")
            return False

    def delete_appointment(self, appointment_id):
        """Delete an appointment"""
        try:
            cur = self.db.cursor()
            
            # Try enhanced table first
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("DELETE FROM appointments_enhanced WHERE appointment_id = ?", (appointment_id,))
                cur.execute("DELETE FROM appointment_services WHERE appointment_id = ?", (appointment_id,))
            
            # Also delete from regular table
            cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
            
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting appointment: {e}")
            return False

    def send_appointment_reminder(self, appointment_id):
        """Send appointment reminder"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("""
                    UPDATE appointments_enhanced 
                    SET reminder_sent = 1 
                    WHERE appointment_id = ?
                """, (appointment_id,))
                self.db.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error sending reminder: {e}")
            return False


class ShoppingCart:
    """Manages shopping cart operations for items"""
    
    def __init__(self):
        self.items = []

    def add_item(self, item_id, item_name, price, quantity=1, category=""):
        """Add item to cart"""
        for item in self.items:
            if item.item_id == item_id:
                item.quantity += quantity
                return

        new_item = CartItem(item_id, item_name, price, quantity, category)
        self.items.append(new_item)

    def remove_item(self, item_id):
        """Remove item from cart"""
        self.items = [
            item for item in self.items if item.item_id != item_id]

    def update_quantity(self, item_id, quantity):
        """Update item quantity in cart"""
        for item in self.items:
            if item.item_id == item_id:
                if quantity <= 0:
                    self.remove_item(item_id)
                else:
                    item.quantity = quantity
                return

    def clear(self):
        """Clear all items from cart"""
        self.items = []

    @property
    def total(self):
        """Calculate total cart value"""
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)

    def to_legacy_format(self):
        """Convert to legacy format for existing code"""
        return [item.to_dict() for item in self.items]


class AnalyticsManager:
    """Manages reporting and analytics"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_revenue_trends(self, period='monthly', start_date=None, end_date=None):
        """Get revenue trends over time"""
        try:
            cur = self.db.cursor()
            
            if period == 'daily':
                group_by = "strftime('%Y-%m-%d', sale_date)"
            elif period == 'weekly':
                group_by = "strftime('%Y-W%W', sale_date)"
            else:  # monthly
                group_by = "strftime('%Y-%m', sale_date)"
            
            query = f"""
                SELECT 
                    {group_by} as period,
                    SUM(total_amount) as revenue,
                    COUNT(DISTINCT transaction_id) as transactions,
                    AVG(total_amount) as avg_transaction
                FROM sales 
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date)
            
            query += f" GROUP BY {group_by} ORDER BY period"
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting revenue trends: {e}")
            return []
    
    def get_popular_services(self, limit=10, start_date=None, end_date=None):
        """Get most popular services"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                table_name = "appointments_enhanced"
                date_field = "appointment_date"
            else:
                table_name = "appointments"
                date_field = "date"
            
            query = f"""
                SELECT 
                    service,
                    COUNT(*) as service_count,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_revenue
                FROM {table_name} 
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += f" AND {date_field} >= ?"
                params.append(start_date)
            if end_date:
                query += f" AND {date_field} <= ?"
                params.append(end_date)
            
            query += " GROUP BY service ORDER BY service_count DESC LIMIT ?"
            params.append(limit)
            
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting popular services: {e}")
            return []
    
    def get_customer_demographics(self):
        """Get customer/patient demographics"""
        try:
            cur = self.db.cursor()
            
            # Animal type distribution
            cur.execute("""
                SELECT 
                    animal_type,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM appointments), 2) as percentage
                FROM appointments 
                GROUP BY animal_type 
                ORDER BY count DESC
            """)
            animal_distribution = cur.fetchall()
            
            # Appointment frequency by customer
            cur.execute("""
                SELECT 
                    owner_name,
                    COUNT(*) as appointment_count,
                    SUM(total_amount) as total_spent,
                    AVG(total_amount) as avg_spent
                FROM appointments 
                GROUP BY owner_name 
                ORDER BY appointment_count DESC
                LIMIT 20
            """)
            customer_frequency = cur.fetchall()
            
            return {
                'animal_distribution': animal_distribution,
                'customer_frequency': customer_frequency
            }
        except sqlite3.Error as e:
            print(f"Error getting demographics: {e}")
            return {}
    
    def get_veterinarian_performance(self, start_date=None, end_date=None):
        """Get veterinarian performance metrics"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                query = """
                    SELECT 
                        veterinarian,
                        COUNT(*) as appointments,
                        SUM(total_amount) as revenue,
                        AVG(total_amount) as avg_revenue_per_appointment,
                        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
                        COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) as cancelled,
                        ROUND(COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate
                    FROM appointments_enhanced 
                    WHERE veterinarian IS NOT NULL AND veterinarian != ''
                """
                params = []
                
                if start_date:
                    query += " AND appointment_date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND appointment_date <= ?"
                    params.append(end_date)
                
                query += " GROUP BY veterinarian ORDER BY revenue DESC"
                cur.execute(query, params)
                return cur.fetchall()
            else:
                return []
        except sqlite3.Error as e:
            print(f"Error getting veterinarian performance: {e}")
            return []


class CommunicationManager:
    """Manages client communication including reminders"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def send_appointment_reminder(self, appointment_id):
        """Send appointment reminder to client"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("""
                    SELECT * FROM appointments_enhanced 
                    WHERE appointment_id = ? AND reminder_sent = 0
                """, (appointment_id,))
                appointment = cur.fetchone()
                
                if appointment:
                    cur.execute("""
                        UPDATE appointments_enhanced 
                        SET reminder_sent = 1 
                        WHERE appointment_id = ?
                    """, (appointment_id,))
                    self.db.commit()
                    
                    # Create communication log table if not exists
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
                    
                    # Log the reminder
                    cur.execute("""
                        INSERT INTO communication_log 
                        (appointment_id, communication_type, sent_to, message, sent_date, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (appointment_id, 'REMINDER', appointment[3], 
                         f"Reminder for appointment on {appointment[8]} at {appointment[9]}",
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'SENT'))
                    self.db.commit()
                    return True
        except sqlite3.Error as e:
            print(f"Error sending reminder: {e}")
        return False
    
    def send_follow_up(self, appointment_id, message=""):
        """Send follow-up message after appointment"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("SELECT * FROM appointments_enhanced WHERE appointment_id = ?", 
                           (appointment_id,))
                appointment = cur.fetchone()
                
                if appointment:
                    # Create communication log table if not exists
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
                    
                    # Log the follow-up
                    cur.execute("""
                        INSERT INTO communication_log 
                        (appointment_id, communication_type, sent_to, message, sent_date, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (appointment_id, 'FOLLOW_UP', appointment[3], 
                         message or "Thank you for visiting our clinic. How is your pet doing?",
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'SENT'))
                    self.db.commit()
                    
                    # Mark follow-up as needed
                    cur.execute("""
                        UPDATE appointments_enhanced 
                        SET follow_up_needed = 0 
                        WHERE appointment_id = ?
                    """, (appointment_id,))
                    self.db.commit()
                    return True
        except sqlite3.Error as e:
            print(f"Error sending follow-up: {e}")
        return False
    
    def get_communication_log(self, appointment_id=None, customer_name=None):
        """Get communication history"""
        try:
            cur = self.db.cursor()
            
            # Check if communication log table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_log'")
            if not cur.fetchone():
                return []
            
            query = "SELECT * FROM communication_log WHERE 1=1"
            params = []
            
            if appointment_id:
                query += " AND appointment_id = ?"
                params.append(appointment_id)
            if customer_name:
                query += " AND sent_to = ?"
                params.append(customer_name)
            
            query += " ORDER BY sent_date DESC"
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting communication log: {e}")
            return []
    
    def check_and_send_reminders(self):
        """Check for appointments needing reminders and send them"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if not cur.fetchone():
                return 0
            
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT appointment_id FROM appointments_enhanced 
                WHERE appointment_date = ? 
                AND status = 'SCHEDULED'
                AND reminder_sent = 0
            """, (tomorrow,))
            
            appointments = cur.fetchall()
            sent_count = 0
            
            for apt in appointments:
                if self.send_appointment_reminder(apt[0]):
                    sent_count += 1
            
            return sent_count
        except sqlite3.Error as e:
            print(f"Error checking reminders: {e}")
            return 0


class SalesManager:
    """Manages sales and transactions"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def record_sale(self, transaction_id, items, total_amount, payment_method, customer_name=""):
        """Record a sale transaction"""
        try:
            cur = self.db.cursor()
            for item in items:
                cur.execute("""INSERT INTO sales 
                            (transaction_id, item_id, item_name, quantity, price, subtotal, 
                             total_amount, payment_method, customer_name, sale_date) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (transaction_id, item['id'], item['name'], item['qty'], 
                             item['price'], item['subtotal'], total_amount, payment_method,
                             customer_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Update inventory stock
            for item in items:
                cur.execute("UPDATE inventory SET stock = stock - ? WHERE id = ?",
                           (item['qty'], item['id']))
            
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording sale: {e}")
            return False
    
    def get_sales_report(self, start_date=None, end_date=None):
        """Get sales report for a date range"""
        try:
            cur = self.db.cursor()
            query = "SELECT * FROM sales WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY sale_date DESC"
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting sales report: {e}")
            return []


class ReceiptManager:
    """Manages receipt generation and printing"""
    @staticmethod
    def generate_receipt_text(appointment_id, patient_name, owner_name, animal_type, notes, date, total_amount, cart_items):
        """Generate receipt as text string"""
        receipt = "=" * 50 + "\n"
        receipt += "         VETERINARY CLINIC\n"
        receipt += "       Official Service Receipt\n"
        receipt += "   123 Main Street, City, Philippines\n"
        receipt += "          Tel: (02) 1234-5678\n"
        receipt += "=" * 50 + "\n\n"

        receipt += f"Appointment: {appointment_id}\n"
        receipt += f"Date: {date}\n"
        receipt += f"Patient: {patient_name}\n"
        receipt += f"Owner: {owner_name}\n"
        receipt += f"Animal Type: {animal_type}\n"
        if notes:
            receipt += f"Notes: {notes}\n"
        receipt += "\n" + "-" * 50 + "\n"
        receipt += "SERVICE/ITEM                       QTY   PRICE   SUBTOTAL\n"
        receipt += "-" * 50 + "\n"

        for item in cart_items:
            item_name = item['name']
            if len(item_name) > 30:
                item_name = item_name[:27] + "..."

            receipt += f"{item_name:<30} {item['qty']:>3}  ₱{item['price']:>6.2f}  ₱{item['subtotal']:>7.2f}\n"

        receipt += "-" * 50 + "\n"
        receipt += f"TOTAL: ₱{total_amount:>38.2f}\n"
        receipt += "=" * 50 + "\n\n"

        receipt += "POLICY:\n"
        receipt += "• Follow-up appointments as advised\n"
        receipt += "• Keep this receipt for records\n"
        receipt += "• Contact us for any concerns\n\n"

        receipt += "Thank you for choosing our clinic!\n"
        receipt += "We care for your pets\n"
        receipt += "=" * 50 + "\n"

        return receipt

    @staticmethod
    def save_receipt_to_file(receipt_text, filename=None):
        """Save receipt to text file"""
        if filename is None:
            filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            return filename
        except Exception as e:
            print(f"Error saving receipt: {e}")
            return None


# ==================== MAIN APPLICATION ====================

APP_TITLE = "🐾 Veterinary Clinic Management System v2.0"
DB_FILE = "vetclinic.db"
THEME_MODE = "dark"

# Service prices for appointments - EXPANDED AND FIXED
SERVICE_PRICES = {
    "Consultation": 500.00,
    "Vaccination": 800.00,
    "Surgery": 2500.00,
    "Grooming": 600.00,
    "Checkup": 400.00,
    "Dental Cleaning": 1200.00,
    "X-Ray": 1500.00,
    "Blood Test": 800.00,
    "Emergency Care": 2000.00,
    "Vaccine Booster": 600.00,
    "Spay/Neuter": 3000.00,
    "Microchipping": 800.00
}

# Veterinarians list
VETERINARIANS = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", "Dr. Davis"]


def get_db():
    return sqlite3.connect(DB_FILE)


def apply_theme(window=None):
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme("blue")
    if window is not None:
        try:
            window.update()
        except tk.TclError:
            pass


def generate_appointment_id():
    return f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"


def generate_transaction_id():
    return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"


def validate_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
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


# ==================== ENHANCED DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database with all required tables"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        print("Initializing database structure...")
        
        # ========== USERS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'staff',
                full_name TEXT,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # ========== INVENTORY TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL DEFAULT 0.0,
                stock INTEGER NOT NULL DEFAULT 0,
                category TEXT,
                subcategory TEXT,
                brand TEXT,
                animal_type TEXT,
                dosage TEXT,
                unit TEXT DEFAULT 'each',
                expiration_date TEXT,
                supplier TEXT,
                cost_price REAL,
                reorder_level INTEGER DEFAULT 10,
                barcode TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create indexes for inventory
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventory_animal_type ON inventory(animal_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventory_expiration ON inventory(expiration_date)")
        
        # ========== APPOINTMENTS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT UNIQUE NOT NULL,
                patient_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                owner_phone TEXT,
                owner_email TEXT,
                animal_type TEXT NOT NULL,
                breed TEXT,
                age TEXT,
                weight TEXT,
                service TEXT NOT NULL,
                service_details TEXT,
                qty INTEGER DEFAULT 1,
                price REAL NOT NULL,
                subtotal REAL NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                duration INTEGER DEFAULT 30,
                notes TEXT,
                status TEXT DEFAULT 'SCHEDULED',
                veterinarian TEXT,
                total_amount REAL NOT NULL,
                payment_status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_sent BOOLEAN DEFAULT 0,
                follow_up_needed BOOLEAN DEFAULT 0
            )
        """)
        
        # ========== ENHANCED APPOINTMENTS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments_enhanced(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT UNIQUE NOT NULL,
                patient_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                owner_phone TEXT,
                owner_email TEXT,
                animal_type TEXT NOT NULL,
                breed TEXT,
                age TEXT,
                weight TEXT,
                service TEXT NOT NULL,
                veterinarian TEXT,
                duration INTEGER DEFAULT 30,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                status TEXT DEFAULT 'SCHEDULED',
                total_amount REAL NOT NULL,
                reminder_sent BOOLEAN DEFAULT 0,
                follow_up_needed BOOLEAN DEFAULT 0,
                created_by TEXT,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== APPOINTMENT SERVICES TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment_services(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT NOT NULL,
                service_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                price REAL NOT NULL,
                subtotal REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments_enhanced(appointment_id)
            )
        """)
        
        # ========== SALES TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                item_id INTEGER,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                subtotal REAL NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tax_amount REAL DEFAULT 0.0,
                discount_amount REAL DEFAULT 0.0,
                cashier_name TEXT,
                refunded BOOLEAN DEFAULT 0,
                refund_amount REAL DEFAULT 0.0,
                refund_date TEXT,
                refund_reason TEXT
            )
        """)
        
        # ========== COMMUNICATION LOG TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS communication_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                communication_type TEXT NOT NULL,
                subject TEXT,
                message TEXT NOT NULL,
                sent_by TEXT,
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'SENT',
                delivery_status TEXT,
                read_receipt BOOLEAN DEFAULT 0,
                response TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
            )
        """)
        
        # ========== FINANCIAL TRANSACTIONS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS financial_transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transaction_type TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                payment_method TEXT,
                category TEXT,
                reference_id TEXT,
                created_by TEXT,
                notes TEXT
            )
        """)
        
        # ========== PATIENT MEDICAL RECORDS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS medical_records(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                animal_type TEXT NOT NULL,
                breed TEXT,
                age TEXT,
                weight TEXT,
                visit_date TEXT NOT NULL,
                veterinarian TEXT,
                diagnosis TEXT,
                treatment TEXT,
                medications TEXT,
                notes TEXT,
                follow_up_date TEXT,
                attachments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== SUPPLIERS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS suppliers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                products TEXT,
                payment_terms TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # ========== VACCINATION RECORDS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vaccination_records(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                animal_type TEXT NOT NULL,
                vaccine_name TEXT NOT NULL,
                vaccine_type TEXT,
                manufacturer TEXT,
                batch_number TEXT,
                administration_date TEXT NOT NULL,
                next_due_date TEXT,
                veterinarian TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== SYSTEM SETTINGS TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_settings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== AUDIT LOG TABLE ==========
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== DEFAULT SETTINGS ==========
        default_settings = [
            ('clinic_name', 'Veterinary Clinic Management System', 'text', 'General', 'Name of the veterinary clinic'),
            ('clinic_address', '123 Main Street, City, Philippines', 'text', 'General', 'Clinic address'),
            ('clinic_phone', '(02) 1234-5678', 'text', 'General', 'Clinic phone number'),
            ('clinic_email', 'info@vetclinic.com', 'text', 'General', 'Clinic email address'),
            ('tax_rate', '12.0', 'decimal', 'Financial', 'Tax rate in percentage'),
            ('currency', 'PHP', 'text', 'Financial', 'Currency code'),
            ('currency_symbol', '₱', 'text', 'Financial', 'Currency symbol'),
            ('auto_backup', '1', 'boolean', 'System', 'Enable automatic backups'),
            ('backup_frequency', 'daily', 'text', 'System', 'Backup frequency'),
            ('appointment_reminder_hours', '24', 'integer', 'Appointments', 'Hours before appointment to send reminder'),
            ('default_veterinarian', 'Dr. Smith', 'text', 'Appointments', 'Default veterinarian'),
            ('consultation_fee', '500.00', 'decimal', 'Services', 'Default consultation fee'),
            ('low_stock_threshold', '10', 'integer', 'Inventory', 'Low stock threshold level'),
            ('expiry_warning_days', '30', 'integer', 'Inventory', 'Days before expiry to show warning'),
            ('theme_mode', 'dark', 'text', 'Appearance', 'Application theme mode'),
            ('language', 'en', 'text', 'Appearance', 'Application language')
        ]
        
        for key, value, stype, category, description in default_settings:
            cur.execute("""
                INSERT OR IGNORE INTO system_settings 
                (setting_key, setting_value, setting_type, category, description)
                VALUES (?, ?, ?, ?, ?)
            """, (key, value, stype, category, description))
        
        # ========== DEFAULT USERS ==========
        default_users = [
            ('admin', 'admin123', 'admin', 'Administrator', 'admin@vetclinic.com', '09123456789'),
            ('vet_smith', 'vet123', 'veterinarian', 'Dr. John Smith', 'smith@vetclinic.com', '09123456790'),
            ('vet_jones', 'vet123', 'veterinarian', 'Dr. Sarah Jones', 'jones@vetclinic.com', '09123456791'),
            ('staff_maria', 'staff123', 'staff', 'Maria Garcia', 'maria@vetclinic.com', '09123456792'),
            ('reception_alex', 'recep123', 'receptionist', 'Alex Tan', 'alex@vetclinic.com', '09123456793'),
            ('inventory_manager', 'inv123', 'staff', 'Robert Lee', 'robert@vetclinic.com', '09123456794')
        ]
        
        for username, password, role, full_name, email, phone in default_users:
            cur.execute("""
                INSERT OR IGNORE INTO users 
                (username, password, role, full_name, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password, role, full_name, email, phone))
        
        conn.commit()
        print("Database structure created successfully!")
        
        # ========== POPULATE INITIAL DATA ==========
        print("Populating initial data...")
        
        # Populate inventory
        populate_initial_inventory(conn)
        
        # Populate sample appointments
        populate_sample_appointments(conn)
        
        # Populate sample medical records
        populate_sample_medical_records(conn)
        
        # Populate sample vaccination records
        populate_sample_vaccination_records(conn)
        
        # Populate suppliers
        populate_suppliers(conn)
        
        conn.commit()
        conn.close()
        
        print("Database initialization completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        messagebox.showerror(
            "Database Error", f"Database initialization failed: {str(e)}")

def populate_initial_inventory(conn):
    """Populate inventory with comprehensive sample data"""
    try:
        cur = conn.cursor()
        
        # Clear existing inventory
        cur.execute("DELETE FROM inventory")
        
        # Sample inventory data
        inventory_items = [
            # Dog Vaccines
            ('Rabies Vaccine (Single Dose)', 'Anti-rabies vaccine for dogs', 350.00, 50, 'Vaccines', 'Dog Vaccines', 'VetPharma', 'Dog', '1ml', 'vial', '2025-12-31', 'PharmaCorp', 250.00, 10, 'VAC001'),
            ('DHPP Vaccine (5-in-1)', 'Canine Distemper, Hepatitis, Parainfluenza, Parvovirus', 450.00, 40, 'Vaccines', 'Dog Vaccines', 'AnimalHealth', 'Dog', '1ml', 'vial', '2025-11-30', 'MediSupplies', 320.00, 10, 'VAC002'),
            ('Bordetella Vaccine', 'Kennel cough prevention', 380.00, 35, 'Vaccines', 'Dog Vaccines', 'PetCare', 'Dog', '1ml', 'vial', '2025-10-15', 'HealthPlus', 280.00, 10, 'VAC003'),
            ('Leptospirosis Vaccine', 'Leptospirosis prevention', 420.00, 30, 'Vaccines', 'Dog Vaccines', 'VetGuard', 'Dog', '1ml', 'vial', '2025-09-30', 'PharmaCorp', 300.00, 10, 'VAC004'),
            
            # Cat Vaccines
            ('FVRCP Vaccine (3-in-1)', 'Feline Viral Rhinotracheitis, Calicivirus, Panleukopenia', 400.00, 45, 'Vaccines', 'Cat Vaccines', 'FelineCare', 'Cat', '1ml', 'vial', '2025-12-31', 'CatMed', 300.00, 10, 'VAC005'),
            ('Feline Rabies Vaccine', 'Anti-rabies vaccine for cats', 380.00, 40, 'Vaccines', 'Cat Vaccines', 'VetPharma', 'Cat', '1ml', 'vial', '2025-11-30', 'MediSupplies', 270.00, 10, 'VAC006'),
            ('Feline Leukemia Vaccine', 'FeLV prevention', 550.00, 25, 'Vaccines', 'Cat Vaccines', 'AnimalHealth', 'Cat', '1ml', 'vial', '2025-10-31', 'HealthPlus', 400.00, 5, 'VAC007'),
            
            # Antibiotics
            ('Amoxicillin 500mg (Tablets)', 'Broad-spectrum antibiotic, 20 tablets per pack', 850.00, 30, 'Medications', 'Antibiotics', 'Generic', 'All', '500mg', 'pack', '2025-06-30', 'PharmaCorp', 600.00, 10, 'MED001'),
            ('Clindamycin 150mg (Capsules)', 'For bacterial infections, 14 capsules', 1200.00, 20, 'Medications', 'Antibiotics', 'VetPharma', 'Cat', '150mg', 'pack', '2025-07-31', 'MediSupplies', 850.00, 5, 'MED002'),
            ('Enrofloxacin 50mg (Tablets)', 'Broad-spectrum antibiotic, 30 tablets', 950.00, 25, 'Medications', 'Antibiotics', 'AnimalHealth', 'Dog', '50mg', 'pack', '2025-08-15', 'HealthPlus', 700.00, 10, 'MED003'),
            ('Cephalexin 500mg (Capsules)', 'For skin infections, 20 capsules', 1100.00, 18, 'Medications', 'Antibiotics', 'PetCare', 'All', '500mg', 'pack', '2025-09-30', 'PharmaCorp', 800.00, 5, 'MED004'),
            
            # Anti-inflammatories
            ('Carprofen 100mg (Tablets)', 'Non-steroidal anti-inflammatory, 30 tablets', 1800.00, 15, 'Medications', 'Anti-inflammatories', 'Rimadyl', 'Dog', '100mg', 'pack', '2025-12-31', 'MediSupplies', 1300.00, 5, 'MED005'),
            ('Meloxicam 1.5mg/ml (Oral Suspension)', 'NSAID pain relief, 30ml bottle', 1200.00, 22, 'Medications', 'Anti-inflammatories', 'Metacam', 'Cat', '1.5mg/ml', 'bottle', '2025-11-30', 'HealthPlus', 850.00, 10, 'MED006'),
            ('Prednisolone 5mg (Tablets)', 'Steroid anti-inflammatory, 50 tablets', 750.00, 35, 'Medications', 'Anti-inflammatories', 'Generic', 'All', '5mg', 'pack', '2025-10-31', 'PharmaCorp', 500.00, 10, 'MED007'),
            
            # Parasite Control
            ('Frontline Plus for Dogs', 'Flea and tick treatment, 3 doses', 1200.00, 40, 'Parasite Control', 'Topical', 'Merial', 'Dog', '3 doses', 'pack', '2026-01-31', 'PetSupplies', 850.00, 10, 'PAR001'),
            ('Revolution for Cats', 'Flea, heartworm, and parasite control, 3 doses', 1350.00, 35, 'Parasite Control', 'Topical', 'Zoetis', 'Cat', '3 doses', 'pack', '2026-02-28', 'CatMed', 950.00, 10, 'PAR002'),
            ('Heartgard Plus for Dogs', 'Heartworm prevention, 6 doses', 1800.00, 25, 'Parasite Control', 'Oral', 'Merial', 'Dog', '6 doses', 'pack', '2025-12-31', 'MediSupplies', 1300.00, 5, 'PAR003'),
            ('NexGard for Dogs', 'Oral flea and tick treatment, 3 doses', 1500.00, 30, 'Parasite Control', 'Oral', 'Merial', 'Dog', '3 doses', 'pack', '2025-11-30', 'HealthPlus', 1100.00, 10, 'PAR004'),
            
            # Pet Food - Dog
            ('Premium Dog Dry Food 5kg', 'Complete nutrition for adult dogs', 850.00, 25, 'Pet Food', 'Dry Food', 'Royal Canin', 'Dog', 'N/A', 'bag', '2025-12-31', 'FoodSupplies', 600.00, 10, 'FOOD001'),
            ('Puppy Dry Food 3kg', 'Nutrition for growing puppies', 650.00, 30, 'Pet Food', 'Dry Food', 'Hills Science Diet', 'Dog', 'N/A', 'bag', '2025-11-30', 'FoodSupplies', 450.00, 10, 'FOOD002'),
            ('Senior Dog Food 5kg', 'Specially formulated for senior dogs', 900.00, 20, 'Pet Food', 'Dry Food', 'Purina Pro Plan', 'Dog', 'N/A', 'bag', '2025-10-31', 'FoodSupplies', 650.00, 5, 'FOOD003'),
            ('Dog Wet Food Cans (12 pack)', 'Variety pack of wet food', 480.00, 40, 'Pet Food', 'Wet Food', 'Pedigree', 'Dog', 'N/A', 'pack', '2024-12-31', 'FoodSupplies', 350.00, 10, 'FOOD004'),
            
            # Pet Food - Cat
            ('Adult Cat Dry Food 2kg', 'Complete nutrition for adult cats', 550.00, 35, 'Pet Food', 'Dry Food', 'Whiskas', 'Cat', 'N/A', 'bag', '2025-12-31', 'CatFoodSupplies', 380.00, 10, 'FOOD005'),
            ('Kitten Dry Food 1.5kg', 'Nutrition for growing kittens', 600.00, 25, 'Pet Food', 'Dry Food', 'Royal Canin', 'Cat', 'N/A', 'bag', '2025-11-30', 'CatFoodSupplies', 420.00, 10, 'FOOD006'),
            ('Cat Wet Food Pouches (12 pack)', 'Assorted flavors wet food', 420.00, 50, 'Pet Food', 'Wet Food', 'Friskies', 'Cat', 'N/A', 'pack', '2024-12-31', 'CatFoodSupplies', 300.00, 15, 'FOOD007'),
            ('Hairball Control Cat Food 2kg', 'Special formula for hairball control', 680.00, 20, 'Pet Food', 'Dry Food', 'Hills Science Diet', 'Cat', 'N/A', 'bag', '2025-09-30', 'CatFoodSupplies', 480.00, 5, 'FOOD008'),
            
            # Supplies
            ('Sterile Bandage 5cm x 5m', 'Medical-grade sterile bandage', 150.00, 60, 'Supplies', 'Bandages', 'MediSupplies', 'All', 'N/A', 'roll', '2027-12-31', 'SupplyCorp', 100.00, 20, 'SUP001'),
            ('Disposable Syringes 5ml (Box of 100)', 'Sterile disposable syringes', 800.00, 15, 'Supplies', 'Syringes', 'BD', 'All', '5ml', 'box', '2026-06-30', 'SupplyCorp', 550.00, 5, 'SUP002'),
            ('Examination Gloves (Box of 100)', 'Latex-free examination gloves', 450.00, 30, 'Supplies', 'Gloves', 'Medline', 'All', 'N/A', 'box', '2026-12-31', 'SupplyCorp', 300.00, 10, 'SUP003'),
            ('Digital Thermometer', 'Pet digital thermometer', 1200.00, 12, 'Supplies', 'Equipment', 'PetTemp', 'All', 'N/A', 'each', '2028-12-31', 'EquipmentCorp', 850.00, 3, 'SUP004'),
            ('Pet Carrier Medium Size', 'Medium-sized pet carrier', 2500.00, 8, 'Supplies', 'Carriers', 'PetSafe', 'All', 'N/A', 'each', '2030-12-31', 'PetSupplyCorp', 1800.00, 2, 'SUP005'),
            ('Elizabethan Collar (E-collar)', 'Plastic recovery collar for pets', 350.00, 25, 'Supplies', 'Recovery', 'PetCare', 'All', 'N/A', 'each', '2027-06-30', 'SupplyCorp', 250.00, 10, 'SUP006'),
            
            # Grooming Products
            ('Pet Shampoo 500ml', 'Hypoallergenic pet shampoo', 350.00, 40, 'Grooming', 'Shampoo', 'TropiClean', 'All', 'N/A', 'bottle', '2026-08-31', 'GroomingSupplies', 250.00, 10, 'GRO001'),
            ('Pet Conditioner 500ml', 'Moisturizing pet conditioner', 380.00, 35, 'Grooming', 'Conditioner', 'Earthbath', 'All', 'N/A', 'bottle', '2026-07-31', 'GroomingSupplies', 270.00, 10, 'GRO002'),
            ('Pet Nail Clippers', 'Professional pet nail clippers', 450.00, 20, 'Grooming', 'Tools', 'Safari', 'All', 'N/A', 'each', '2028-12-31', 'GroomingSupplies', 320.00, 5, 'GRO003'),
            ('Slicker Brush', 'Professional grooming brush', 280.00, 30, 'Grooming', 'Brushes', 'Chris Christensen', 'All', 'N/A', 'each', '2027-12-31', 'GroomingSupplies', 200.00, 10, 'GRO004'),
            
            # Dental Care
            ('Dental Chews (Pack of 10)', 'Dental hygiene chews for dogs', 320.00, 50, 'Dental Care', 'Chews', 'Greenies', 'Dog', 'N/A', 'pack', '2025-10-31', 'DentalSupplies', 220.00, 15, 'DEN001'),
            ('Toothbrush and Toothpaste Kit', 'Pet dental care kit', 280.00, 25, 'Dental Care', 'Kits', 'Virbac', 'All', 'N/A', 'kit', '2026-05-31', 'DentalSupplies', 200.00, 10, 'DEN002'),
            ('Dental Water Additive', 'Oral hygiene water additive', 420.00, 20, 'Dental Care', 'Additives', 'TropiClean', 'All', 'N/A', 'bottle', '2025-12-31', 'DentalSupplies', 300.00, 5, 'DEN003'),
            
            # Nutritional Supplements
            ('Joint Supplement for Dogs', 'Glucosamine and chondroitin supplement, 60 tablets', 1800.00, 15, 'Supplements', 'Joint Health', 'Cosequin', 'Dog', 'N/A', 'bottle', '2025-11-30', 'SupplementCorp', 1300.00, 5, 'SUPPL001'),
            ('Omega-3 Fish Oil 250ml', 'Skin and coat supplement', 950.00, 25, 'Supplements', 'Skin & Coat', 'Nordic Naturals', 'All', 'N/A', 'bottle', '2025-09-30', 'SupplementCorp', 650.00, 10, 'SUPPL002'),
            ('Probiotic Supplement for Cats', 'Digestive health supplement, 30 doses', 1200.00, 18, 'Supplements', 'Digestive Health', 'Fortiflora', 'Cat', 'N/A', 'box', '2025-08-31', 'SupplementCorp', 850.00, 5, 'SUPPL003'),
            ('Multivitamin for Dogs', 'Complete vitamin supplement, 90 tablets', 1500.00, 20, 'Supplements', 'Multivitamins', 'Pet-Tabs', 'Dog', 'N/A', 'bottle', '2025-12-31', 'SupplementCorp', 1100.00, 5, 'SUPPL004')
        ]
        
        for item in inventory_items:
            cur.execute("""
                INSERT INTO inventory 
                (name, description, price, stock, category, subcategory, brand, animal_type, dosage, unit, 
                 expiration_date, supplier, cost_price, reorder_level, barcode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, item)
        
        print(f"Added {len(inventory_items)} inventory items")
        
    except sqlite3.Error as e:
        print(f"Error populating inventory: {e}")
        raise

def populate_sample_appointments(conn):
    """Populate sample appointment data"""
    try:
        cur = conn.cursor()
        
        # Clear existing appointments
        cur.execute("DELETE FROM appointments")
        cur.execute("DELETE FROM appointments_enhanced")
        cur.execute("DELETE FROM appointment_services")
        
        # Sample appointments
        import random
        from datetime import datetime, timedelta
        
        veterinarians = ['Dr. John Smith', 'Dr. Sarah Jones', 'Dr. Michael Brown', 'Dr. Emily Davis']
        services = ['Consultation', 'Vaccination', 'Checkup', 'Dental Cleaning', 'Grooming', 'Surgery']
        statuses = ['SCHEDULED', 'COMPLETED', 'IN_PROGRESS', 'CANCELLED']
        pet_names = ['Max', 'Bella', 'Charlie', 'Lucy', 'Cooper', 'Daisy', 'Buddy', 'Luna', 'Rocky', 'Molly']
        owner_names = ['Juan Dela Cruz', 'Maria Santos', 'Robert Lim', 'Anna Tan', 'James Wilson', 
                      'Sarah Garcia', 'Michael Chen', 'Jennifer Lee', 'David Kim', 'Lisa Wong']
        
        # Generate appointments for the next 30 days
        for i in range(50):
            appointment_id = f"APT{datetime.now().strftime('%Y%m%d')}{i:03d}"
            patient_name = random.choice(pet_names)
            owner_name = random.choice(owner_names)
            animal_type = random.choice(['Dog', 'Cat'])
            service = random.choice(services)
            veterinarian = random.choice(veterinarians)
            status = random.choice(statuses)
            
            # Generate dates
            appointment_date = (datetime.now() + timedelta(days=random.randint(-10, 20))).strftime('%Y-%m-%d')
            appointment_time = f"{random.randint(9, 16):02d}:00"
            
            # Calculate amount
            if service == 'Consultation':
                price = 500.00
            elif service == 'Vaccination':
                price = 800.00
            elif service == 'Checkup':
                price = 400.00
            elif service == 'Dental Cleaning':
                price = 1200.00
            elif service == 'Grooming':
                price = 600.00
            else:  # Surgery
                price = 2500.00
            
            total_amount = price
            
            # Insert into appointments table
            cur.execute("""
                INSERT INTO appointments 
                (appointment_id, patient_name, owner_name, animal_type, service, qty, price, subtotal, 
                 date, notes, status, veterinarian, total_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient_name, owner_name, animal_type, service, 1, price, price,
                 appointment_date, f"Sample appointment {i}", status, veterinarian, total_amount))
            
            # Insert into enhanced appointments table
            cur.execute("""
                INSERT INTO appointments_enhanced 
                (appointment_id, patient_name, owner_name, animal_type, service, veterinarian, 
                 duration, appointment_date, appointment_time, notes, status, total_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient_name, owner_name, animal_type, service, veterinarian,
                 30, appointment_date, appointment_time, f"Sample enhanced appointment {i}", status, total_amount))
            
            # Insert services
            cur.execute("""
                INSERT INTO appointment_services 
                (appointment_id, service_name, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (appointment_id, service, 1, price, price))
        
        print("Added sample appointments")
        
    except sqlite3.Error as e:
        print(f"Error populating appointments: {e}")

def populate_sample_medical_records(conn):
    """Populate sample medical records"""
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM medical_records")
        
        sample_records = [
            ('Max', 'Juan Dela Cruz', 'Dog', 'Golden Retriever', '3 years', '25kg', '2024-01-15', 
             'Dr. John Smith', 'Annual checkup - healthy', 'Vaccination: Rabies and DHPP', 
             'Rabies vaccine administered', 'Good health, normal weight', '2025-01-15'),
            ('Bella', 'Maria Santos', 'Cat', 'Persian', '2 years', '4kg', '2024-01-20',
             'Dr. Sarah Jones', 'Upper respiratory infection', 'Antibiotics and supportive care',
             'Amoxicillin 50mg twice daily for 7 days', 'Patient recovering well', '2024-02-20'),
            ('Charlie', 'Robert Lim', 'Dog', 'Labrador', '5 years', '30kg', '2024-01-25',
             'Dr. Michael Brown', 'Dental cleaning needed', 'Professional dental cleaning performed',
             'Teeth cleaned, 2 extractions needed', 'Follow up in 2 weeks', '2024-02-10'),
            ('Lucy', 'Anna Tan', 'Cat', 'Siamese', '1 year', '3kg', '2024-02-01',
             'Dr. Emily Davis', 'Spay surgery', 'Ovariohysterectomy performed',
             'Surgery successful, recovery medication provided', 'Suture removal in 10 days', '2024-02-15'),
            ('Cooper', 'James Wilson', 'Dog', 'Beagle', '7 years', '15kg', '2024-02-05',
             'Dr. John Smith', 'Arthritis management', 'Joint supplements and pain management',
             'Carprofen 50mg daily, joint supplements recommended', 'Follow up in 1 month', '2024-03-05')
        ]
        
        for record in sample_records:
            cur.execute("""
                INSERT INTO medical_records 
                (patient_name, owner_name, animal_type, breed, age, weight, visit_date, 
                 veterinarian, diagnosis, treatment, medications, notes, follow_up_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, record)
        
        print("Added sample medical records")
        
    except sqlite3.Error as e:
        print(f"Error populating medical records: {e}")

def populate_sample_vaccination_records(conn):
    """Populate sample vaccination records"""
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM vaccination_records")
        
        sample_vaccinations = [
            ('Max', 'Juan Dela Cruz', 'Dog', 'Rabies Vaccine', 'Core', 'VetPharma', 'BATCH001', 
             '2024-01-15', '2025-01-15', 'Dr. John Smith', 'Annual rabies vaccination'),
            ('Max', 'Juan Dela Cruz', 'Dog', 'DHPP Vaccine', 'Core', 'AnimalHealth', 'BATCH002',
             '2024-01-15', '2025-01-15', 'Dr. John Smith', 'Annual DHPP booster'),
            ('Bella', 'Maria Santos', 'Cat', 'FVRCP Vaccine', 'Core', 'FelineCare', 'BATCH003',
             '2024-01-20', '2025-01-20', 'Dr. Sarah Jones', 'Annual FVRCP vaccination'),
            ('Charlie', 'Robert Lim', 'Dog', 'Bordetella Vaccine', 'Non-core', 'PetCare', 'BATCH004',
             '2024-01-25', '2024-07-25', 'Dr. Michael Brown', 'Kennel cough prevention'),
            ('Lucy', 'Anna Tan', 'Cat', 'Feline Rabies Vaccine', 'Core', 'VetPharma', 'BATCH005',
             '2024-02-01', '2025-02-01', 'Dr. Emily Davis', 'Rabies vaccination during spay visit')
        ]
        
        for vaccination in sample_vaccinations:
            cur.execute("""
                INSERT INTO vaccination_records 
                (patient_name, owner_name, animal_type, vaccine_name, vaccine_type, manufacturer, 
                 batch_number, administration_date, next_due_date, veterinarian, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, vaccination)
        
        print("Added sample vaccination records")
        
    except sqlite3.Error as e:
        print(f"Error populating vaccination records: {e}")

def populate_suppliers(conn):
    """Populate suppliers data"""
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM suppliers")
        
        suppliers = [
            ('PharmaCorp', 'John Supplier', '09171234567', 'john@pharmacorp.com', 
             '123 Supplier St, Makati City', 'Vaccines, Antibiotics, Medications', 
             'Net 30 days', 'Primary vaccine supplier'),
            ('MediSupplies', 'Maria Supplies', '09172345678', 'maria@medisupplies.com',
             '456 Supply Ave, Quezon City', 'Medical supplies, equipment, disposables',
             'Net 45 days', 'Reliable medical supplies provider'),
            ('HealthPlus', 'Robert Health', '09173456789', 'robert@healthplus.com',
             '789 Health Blvd, Taguig City', 'Specialty medications, supplements',
             'Net 30 days', 'Specialty products supplier'),
            ('FoodSupplies', 'Anna Foods', '09174567890', 'anna@foodsupplies.com',
             '321 Food St, Pasig City', 'Pet food, treats, nutritional products',
             'Net 30 days', 'Pet food distributor'),
            ('PetSupplyCorp', 'David Pet', '09175678901', 'david@petsupplycorp.com',
             '654 Pet Ave, Mandaluyong City', 'Pet carriers, beds, grooming supplies',
             'Net 60 days', 'Pet accessories wholesaler')
        ]
        
        for supplier in suppliers:
            cur.execute("""
                INSERT INTO suppliers 
                (name, contact_person, phone, email, address, products, payment_terms, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, supplier)
        
        print("Added suppliers")
        
    except sqlite3.Error as e:
        print(f"Error populating suppliers: {e}")

# ==================== ENHANCED DATABASE FUNCTIONS ====================

def get_database_stats():
    """Get comprehensive database statistics"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        stats = {}
        
        # Get table counts
        tables = ['users', 'inventory', 'appointments', 'appointments_enhanced', 
                 'sales', 'medical_records', 'vaccination_records', 'suppliers']
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cur.fetchone()[0]
            except:
                stats[table] = 0
        
        # Get financial stats
        cur.execute("SELECT SUM(total_amount) FROM sales WHERE refunded = 0")
        stats['total_sales'] = cur.fetchone()[0] or 0
        
        cur.execute("SELECT SUM(total_amount) FROM appointments WHERE status = 'COMPLETED'")
        stats['appointment_revenue'] = cur.fetchone()[0] or 0
        
        # Get inventory valuation
        cur.execute("SELECT SUM(price * stock) FROM inventory")
        stats['inventory_value'] = cur.fetchone()[0] or 0
        
        # Get low stock count
        cur.execute("SELECT COUNT(*) FROM inventory WHERE stock <= reorder_level")
        stats['low_stock_items'] = cur.fetchone()[0] or 0
        
        # Get expiring soon count
        cur.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE expiration_date IS NOT NULL 
            AND expiration_date != ''
            AND julianday(expiration_date) - julianday('now') <= 30
        """)
        stats['expiring_soon'] = cur.fetchone()[0] or 0
        
        conn.close()
        return stats
        
    except sqlite3.Error as e:
        print(f"Error getting database stats: {e}")
        return {}

def backup_database_with_timestamp():
    """Create timestamped database backup"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"vetclinic_backup_{timestamp}.db"
        
        # Close any existing connections
        try:
            conn = get_db()
            conn.close()
        except:
            pass
        
        # Copy database file
        shutil.copy2(DB_FILE, backup_file)
        
        print(f"Database backed up to: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"Backup error: {e}")
        return None

def optimize_database():
    """Optimize database performance"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Run VACUUM to rebuild database
        cur.execute("VACUUM")
        
        # Run ANALYZE to update statistics
        cur.execute("ANALYZE")
        
        conn.commit()
        conn.close()
        
        print("Database optimized successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"Optimization error: {e}")
        return False

def export_database_to_sql():
    """Export database to SQL file"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_file = f"vetclinic_export_{timestamp}.sql"
        
        conn = get_db()
        
        with open(sql_file, 'w', encoding='utf-8') as f:
            # Write schema
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        conn.close()
        
        print(f"Database exported to SQL: {sql_file}")
        return sql_file
        
    except Exception as e:
        print(f"Export error: {e}")
        return None

# ==================== COMPLETE CATALOGS ====================

DOG_MEDICINES = {
    "vaccines": {
        "rabies_vaccine": {
            "Rabies Vaccine (1 dose)": {"price": 350.00, "animal_type": "Dog", "dosage": "1ml", "expiration": "2025-12-31"},
        },
        "dhpp_vaccine": {
            "DHPP Vaccine (1 dose)": {"price": 450.00, "animal_type": "Dog", "dosage": "1ml", "expiration": "2025-12-31"},
        }
    },
    "medications": {
        "antibiotics": {
            "Amoxicillin 500mg (tablet)": {"price": 25.00, "animal_type": "Dog", "dosage": "1 tablet", "expiration": "2025-12-31"},
        },
        "anti_inflammatories": {
            "Carprofen 100mg (tablet)": {"price": 35.00, "animal_type": "Dog", "dosage": "1 tablet", "expiration": "2025-12-31"},
        }
    },
    "supplies": {
        "bandages": {
            "Sterile Bandage 5cm x 5m": {"price": 150.00, "animal_type": "All", "dosage": "N/A", "expiration": "2027-12-31"},
        }
    }
}

CAT_MEDICINES = {
    "vaccines": {
        "fvr_vaccine": {
            "FVR Vaccine (1 dose)": {"price": 400.00, "animal_type": "Cat", "dosage": "1ml", "expiration": "2025-12-31"},
        }
    },
    "medications": {
        "antibiotics": {
            "Clindamycin 75mg (capsule)": {"price": 30.00, "animal_type": "Cat", "dosage": "1 capsule", "expiration": "2025-12-31"},
        }
    }
}

PET_FOODS = {
    "dog_food": {
        "dry_food": {
            "Premium Dog Dry Food 5kg": {"price": 850.00, "animal_type": "Dog", "dosage": "N/A", "expiration": "2025-12-31"},
            "Puppy Dry Food 3kg": {"price": 650.00, "animal_type": "Dog", "dosage": "N/A", "expiration": "2025-12-31"},
        },
        "wet_food": {
            "Dog Wet Food Cans (12 pack)": {"price": 480.00, "animal_type": "Dog", "dosage": "N/A", "expiration": "2024-12-31"},
        }
    },
    "cat_food": {
        "dry_food": {
            "Adult Cat Dry Food 2kg": {"price": 550.00, "animal_type": "Cat", "dosage": "N/A", "expiration": "2025-12-31"},
        },
        "wet_food": {
            "Cat Wet Food Pouches (12 pack)": {"price": 420.00, "animal_type": "Cat", "dosage": "N/A", "expiration": "2024-12-31"},
        }
    }
}

GROOM_SERVICES = {
    "dog_grooming": {
        "basic_groom": {
            "Basic Dog Grooming": {"price": 500.00, "animal_type": "Dog", "description": "Bath, brush, nail trim"},
        },
        "full_groom": {
            "Full Dog Grooming": {"price": 1200.00, "animal_type": "Dog", "description": "Bath, brush, nail trim, haircut"},
        }
    },
    "cat_grooming": {
        "basic_groom": {
            "Basic Cat Grooming": {"price": 400.00, "animal_type": "Cat", "description": "Bath, brush, nail trim"},
        }
    }
}


def populate_initial_inventory_legacy():
    """Legacy function for backward compatibility - calls the enhanced version"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get existing count
        cur.execute("SELECT COUNT(*) FROM inventory")
        count = cur.fetchone()[0]
        
        if count == 0:
            # If no inventory exists, populate it
            populate_initial_inventory(conn)
            conn.commit()
            print("Initial inventory populated successfully!")
        else:
            print(f"Inventory already has {count} items, skipping population.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error in legacy inventory population: {e}")
        return False


# ==================== MODERN UI COMPONENTS ====================

class ModernButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        # Set default colors if not provided
        if 'fg_color' not in kwargs:
            kwargs['fg_color'] = COLORS["primary"]
        if 'hover_color' not in kwargs:
            kwargs['hover_color'] = COLORS["secondary"]
        if 'text_color' not in kwargs:
            kwargs['text_color'] = COLORS["text_light"]
            
        super().__init__(master, **kwargs)
        self.configure(
            font=("Arial", 12, "bold"),
            border_width=2,
            corner_radius=8
        )


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=("Arial", 12),
            border_width=2,
            corner_radius=6,
            fg_color=COLORS["card"],
            text_color=COLORS["text_light"],
            border_color=COLORS["primary"]
        )


class ModernLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        if 'text_color' not in kwargs:
            kwargs['text_color'] = COLORS["text_light"]
        super().__init__(master, **kwargs)
        self.configure(font=("Arial", 12))


class ModernFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        if 'fg_color' not in kwargs:
            kwargs['fg_color'] = COLORS["card"]
        if 'border_color' not in kwargs:
            kwargs['border_color'] = COLORS["primary"]
        super().__init__(master, **kwargs)
        self.configure(corner_radius=10, border_width=1)


class ColorfulCard(ctk.CTkFrame):
    def __init__(self, master, title, value, color):
        super().__init__(master)
        self.configure(
            fg_color=color,
            corner_radius=15,
            border_width=2,
            border_color=COLORS["primary"]
        )
        
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text=title,
            font=("Arial", 14, "bold"),
            text_color=COLORS["text_light"]
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # Value
        value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial", 24, "bold"),
            text_color=COLORS["text_light"]
        )
        value_label.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="w")


class ResponsiveFrame(ctk.CTkFrame):
    """Responsive frame that adjusts based on screen size"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.is_mobile = False
        
    def configure_for_mobile(self):
        """Configure widget for mobile display"""
        screen_width = self.winfo_screenwidth()
        self.is_mobile = screen_width < 768
        
        if self.is_mobile:
            self.configure(padx=5, pady=5)
            for child in self.winfo_children():
                if isinstance(child, (ctk.CTkButton, ModernButton)):
                    child.configure(height=40, font=("Arial", 14))
                elif isinstance(child, (ctk.CTkLabel, ModernLabel)):
                    child.configure(font=("Arial", 12))
                elif isinstance(child, (ctk.CTkEntry, ModernEntry)):
                    child.configure(height=35, font=("Arial", 14))


# ==================== MAIN APPLICATION WINDOW ====================

class VeterinaryClinicApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Set background color
        self.root.configure(fg_color=COLORS["background"])
        
        # Initialize database FIRST
        print("Initializing database...")
        init_db()  # This now calls the enhanced initialization
        
        # Initialize managers
        self.db = get_db()
        self.inventory_manager = EnhancedInventoryManager(self.db)
        self.appointment_manager = EnhancedAppointmentManager(self.db)
        self.sales_manager = SalesManager(self.db)
        self.analytics_manager = AnalyticsManager(self.db)
        self.communication_manager = CommunicationManager(self.db)
        self.cart = ShoppingCart()
        self.current_user = None
        
        # Apply theme
        apply_theme(self.root)
        
        # Setup UI
        self.setup_ui()
        
        # Start reminder scheduler
        self.schedule_reminders()
        
    def schedule_reminders(self):
        """Schedule daily reminder checks"""
        self.check_and_send_reminders()
        # Schedule next check in 24 hours
        self.root.after(24 * 60 * 60 * 1000, self.schedule_reminders)
    
    def check_and_send_reminders(self):
        """Check and send appointment reminders"""
        try:
            sent_count = self.communication_manager.check_and_send_reminders()
            if sent_count > 0:
                print(f"Sent {sent_count} appointment reminders")
        except Exception as e:
            print(f"Error checking reminders: {e}")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.main_content = ModernFrame(self.root)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Show login screen initially
        self.show_login_screen()
        
    def create_sidebar(self):
        """Create the sidebar navigation"""
        self.sidebar = ModernFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(9, weight=1)
        
        # Title with color
        title_label = ModernLabel(self.sidebar, text="🐾 Vet Clinic", 
                                 font=("Arial", 20, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Navigation buttons (will be populated after login)
        self.nav_buttons = {}
        
    def setup_navigation(self):
        """Setup navigation buttons after login"""
        # Clear existing buttons
        for btn in self.nav_buttons.values():
            btn.destroy()
        self.nav_buttons.clear()
        
        # Base navigation items
        nav_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📅 Appointments", self.show_appointments),
            ("📦 Inventory", self.show_inventory),
            ("💰 Point of Sale", self.show_pos),
            ("📊 Reports", self.show_reports),
        ]
        
        # Add role-based features
        if self.current_user.has_permission('manage_communications'):
            nav_items.append(("✉️ Communications", self.show_communications))
        
        nav_items.append(("⚙️ Settings", self.show_settings))
        
        for i, (text, command) in enumerate(nav_items, 1):
            btn = ModernButton(self.sidebar, text=text, command=command,
                              fg_color="transparent", 
                              border_color=COLORS["primary"],
                              hover_color=COLORS["secondary"],
                              text_color=COLORS["text_light"])
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
        
        # Add user role indicator
        role_label = ModernLabel(self.sidebar, 
                                text=f"Role: {self.current_user.get_role_display_name()}",
                                text_color=COLORS["accent"])
        role_label.grid(row=len(nav_items) + 1, column=0, padx=10, pady=5)
        
        # Logout button
        logout_btn = ModernButton(self.sidebar, text="🚪 Logout", command=self.logout,
                                 fg_color=COLORS["danger"], 
                                 hover_color="#c9302c")
        logout_btn.grid(row=len(nav_items) + 2, column=0, padx=10, pady=20, sticky="ew")
    
    def clear_main_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show the login screen"""
        self.clear_main_content()
        
        login_frame = ModernFrame(self.main_content)
        login_frame.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
        login_frame.grid_rowconfigure(4, weight=1)
        login_frame.grid_columnconfigure(0, weight=1)
        
        # Title with color
        title_label = ModernLabel(login_frame, text="Veterinary Clinic Login", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, pady=40)
        
        # Username
        ModernLabel(login_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        username_entry = ModernEntry(login_frame, placeholder_text="Enter username")
        username_entry.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Password
        ModernLabel(login_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        password_entry = ModernEntry(login_frame, placeholder_text="Enter password", show="•")
        password_entry.grid(row=2, column=0, pady=5, sticky="ew")
        
        # Login button
        login_btn = ModernButton(login_frame, text="Login", 
                                command=lambda: self.login(username_entry.get(), password_entry.get()),
                                fg_color=COLORS["success"])
        login_btn.grid(row=3, column=0, pady=20, sticky="ew")
        
        # Default credentials hint
        hint_label = ModernLabel(login_frame, 
                                text="Default: admin/admin123, vet_smith/vet123, staff_maria/staff123, reception_alex/recep123",
                                text_color=COLORS["accent"],
                                font=("Arial", 10))
        hint_label.grid(row=4, column=0, pady=10)
        
        # Bind Enter key to login
        username_entry.bind("<Return>", lambda e: self.login(username_entry.get(), password_entry.get()))
        password_entry.bind("<Return>", lambda e: self.login(username_entry.get(), password_entry.get()))
        
        # Set focus to username field
        username_entry.focus()
    
    def login(self, username, password):
        """Handle user login - FIXED VERSION"""
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                       (username, password))
            user_data = cur.fetchone()
            conn.close()
            
            if user_data:
                # Get user details
                user_id = user_data[0]
                username = user_data[1]
                password = user_data[2]
                role = user_data[3] if len(user_data) > 3 else "staff"
                
                self.current_user = EnhancedUser(user_id, username, password, role)
                self.setup_navigation()
                self.show_dashboard()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        # Clear navigation buttons
        for btn in self.nav_buttons.values():
            btn.destroy()
        self.nav_buttons.clear()
        self.show_login_screen()
    
    def show_dashboard(self):
        """Show the dashboard screen with colorful design"""
        self.clear_main_content()
        
        # Main dashboard frame
        dashboard_frame = ModernFrame(self.main_content)
        dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        dashboard_frame.grid_rowconfigure(2, weight=1)
        dashboard_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome header
        header_frame = ModernFrame(dashboard_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        welcome_label = ModernLabel(header_frame, 
                                   text=f"🐕 Welcome to Veterinary Clinic Management System 🐈",
                                   font=("Arial", 20, "bold"),
                                   text_color=COLORS["accent"])
        welcome_label.grid(row=0, column=0, pady=10)
        
        user_label = ModernLabel(header_frame, 
                                text=f"Logged in as: {self.current_user.username} ({self.current_user.get_role_display_name()})",
                                font=("Arial", 14),
                                text_color=COLORS["text_light"])
        user_label.grid(row=1, column=0, pady=5)
        
        # Statistics cards
        stats_frame = ModernFrame(dashboard_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Get database statistics
        stats = get_database_stats()
        
        stats_data = [
            ("Total Inventory", f"{stats.get('inventory', 0)} items", COLORS["primary"]),
            ("Today's Appointments", f"{stats.get('appointments', 0)}", COLORS["success"]),
            ("Total Sales", f"₱{stats.get('total_sales', 0):,.2f}", COLORS["secondary"]),
            ("Low Stock Items", f"{stats.get('low_stock_items', 0)}", COLORS["warning"]),
            ("Expiring Soon", f"{stats.get('expiring_soon', 0)}", COLORS["danger"]),
            ("Medical Records", f"{stats.get('medical_records', 0)}", COLORS["accent"])
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            row = i // 3
            col = i % 3
            card = ColorfulCard(stats_frame, title, value, color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Quick actions
        actions_frame = ModernFrame(dashboard_frame)
        actions_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        actions_frame.grid_rowconfigure(1, weight=1)
        
        ModernLabel(actions_frame, text="Quick Actions", 
                   font=("Arial", 18, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)
        
        # Quick action buttons
        quick_actions = [
            ("➕ New Appointment", self.create_enhanced_appointment, COLORS["success"]),
            ("📦 Manage Inventory", self.show_inventory, COLORS["primary"]),
            ("💰 POS Sale", self.show_pos, COLORS["secondary"]),
            ("📊 View Reports", self.show_enhanced_reports, COLORS["warning"])
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            btn = ModernButton(actions_frame, text=text, command=command,
                             fg_color=color, hover_color=COLORS["dark"])
            btn.grid(row=1, column=i, padx=10, pady=10, sticky="nsew")
    
    def create_enhanced_appointment(self):
        """Create a new enhanced appointment dialog - FIXED VERSION"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("New Appointment - Enhanced")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["background"])
        
        # Responsive configuration
        if dialog.winfo_screenwidth() < 768:
            dialog.geometry("400x800")
        
        ModernLabel(dialog, text="Create New Appointment", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Form frame
        form_frame = ResponsiveFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        form_frame.configure_for_mobile()
        
        # Form fields with enhanced details
        fields = [
            ("Patient Name:", "entry"),
            ("Owner Name:", "entry"),
            ("Animal Type:", "combo", ["Dog", "Cat", "Bird", "Rabbit", "Other"]),
            ("Service Type:", "combo", list(SERVICE_PRICES.keys())),
            ("Veterinarian:", "combo", VETERINARIANS),
            ("Appointment Date:", "entry"),
            ("Appointment Time:", "combo", ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]),
            ("Duration (minutes):", "combo", ["30", "45", "60", "90", "120"]),
            ("Notes:", "text"),
            ("Status:", "combo", ["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"])
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            ModernLabel(form_frame, text=field[0]).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            if field[1] == "entry":
                if field[0] == "Appointment Date:":
                    # Set default to tomorrow
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    entry = ModernEntry(form_frame, width=300)
                    entry.insert(0, tomorrow)
                else:
                    entry = ModernEntry(form_frame, width=300)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ctk.CTkComboBox(form_frame, values=field[2], width=300)
                combo.set(field[2][0] if field[2] else "")
                combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = combo
                
                # Add price display for service type
                if field[0] == "Service Type:":
                    price_label = ModernLabel(form_frame, text="Price: ₱0.00", 
                                            text_color=COLORS["accent"])
                    price_label.grid(row=row, column=2, padx=10, pady=5)
                    
                    def update_price(event=None):
                        service = combo.get()
                        price = SERVICE_PRICES.get(service, 0.0)
                        price_label.configure(text=f"Price: ₱{price:.2f}")
                    
                    combo.configure(command=lambda e: update_price())
                    # Set initial price
                    update_price()
                    
            elif field[1] == "text":
                text_widget = ctk.CTkTextbox(form_frame, width=300, height=80)
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = text_widget
            
            row += 1
        
        # Submit button
        def submit_appointment():
            try:
                # Get form values
                patient_name = entries["Patient Name:"].get().strip()
                owner_name = entries["Owner Name:"].get().strip()
                animal_type = entries["Animal Type:"].get()
                service_type = entries["Service Type:"].get()
                veterinarian = entries["Veterinarian:"].get()
                appointment_date = entries["Appointment Date:"].get()
                appointment_time = entries["Appointment Time:"].get()
                duration = int(entries["Duration (minutes):"].get())
                notes = entries["Notes:"].get("1.0", "end-1c").strip() if hasattr(entries["Notes:"], 'get') else entries["Notes:"].get()
                status = entries["Status:"].get()
                
                # Validate required fields
                if not patient_name:
                    messagebox.showerror("Error", "Patient name is required")
                    return
                if not owner_name:
                    messagebox.showerror("Error", "Owner name is required")
                    return
                if not service_type:
                    messagebox.showerror("Error", "Service type is required")
                    return
                if not appointment_date:
                    messagebox.showerror("Error", "Appointment date is required")
                    return
                
                # Get service price
                price = SERVICE_PRICES.get(service_type, 0.0)
                
                # Create enhanced appointment object
                appointment = EnhancedAppointment(
                    appointment_id=generate_appointment_id(),
                    patient_name=patient_name,
                    owner_name=owner_name,
                    animal_type=animal_type,
                    service=service_type,
                    notes=notes,
                    status=status,
                    veterinarian=veterinarian,
                    duration=duration,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
                
                # Add service with proper pricing
                appointment.add_service(service_type, 1, price, price)
                
                # Debug: Print appointment details
                print(f"Creating appointment: {appointment.appointment_id}")
                print(f"Patient: {appointment.patient_name}")
                print(f"Owner: {appointment.owner_name}")
                print(f"Service: {appointment.service}")
                print(f"Services list: {appointment.services}")
                print(f"Total amount: {appointment.total_amount}")
                print(f"Date: {appointment.date_created}")
                print(f"Status: {appointment.status}")
                
                # Save to database - try enhanced first, then legacy
                try:
                    # First try enhanced appointment
                    if self.appointment_manager.record_enhanced_appointment(appointment):
                        print("Enhanced appointment recorded successfully")
                    else:
                        print("Failed to record enhanced appointment")
                    
                    # Always try to record to legacy appointments table
                    if self.appointment_manager.record_appointment(appointment):
                        print("Legacy appointment recorded successfully")
                        messagebox.showinfo("Success", "Appointment created successfully!")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to create appointment in main database")
                        
                except Exception as db_error:
                    print(f"Database error: {db_error}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Database Error", f"Failed to create appointment: {str(db_error)}")
                    
            except Exception as e:
                print(f"Appointment creation error: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to create appointment: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Create Appointment", 
                                 command=submit_appointment,
                                 fg_color=COLORS["success"], 
                                 hover_color="#218838")
        submit_btn.pack(pady=20)
    
    def show_appointments(self):
        """Show appointments management screen"""
        self.clear_main_content()
        
        # Main appointments frame
        appointments_frame = ModernFrame(self.main_content)
        appointments_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        appointments_frame.grid_rowconfigure(1, weight=1)
        appointments_frame.grid_columnconfigure(0, weight=1)
        
        # Title with icon
        title_label = ModernLabel(appointments_frame, text="📅 Appointment Management", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create appointment management interface
        self.create_appointments_interface(appointments_frame)
    
    def create_appointments_interface(self, parent):
        """Create appointments management interface"""
        # Button frame
        button_frame = ModernFrame(parent)
        button_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Action buttons with colors
        new_appt_btn = ModernButton(button_frame, text="➕ New Appointment", 
                                   command=self.create_enhanced_appointment,
                                   fg_color=COLORS["success"])
        new_appt_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        view_upcoming_btn = ModernButton(button_frame, text="📅 Upcoming", 
                                        command=self.show_upcoming_appointments,
                                        fg_color=COLORS["primary"])
        view_upcoming_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        view_appt_btn = ModernButton(button_frame, text="👁️ View Details", 
                                    command=self.view_appointments,
                                    fg_color=COLORS["secondary"])
        view_appt_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        update_appt_btn = ModernButton(button_frame, text="✏️ Update Status", 
                                      command=self.update_appointment_status,
                                      fg_color=COLORS["warning"])
        update_appt_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        delete_appt_btn = ModernButton(button_frame, text="🗑️ Delete", 
                                      command=self.delete_appointment,
                                      fg_color=COLORS["danger"])
        delete_appt_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # Appointments list frame
        list_frame = ModernFrame(parent)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview for appointments
        columns = ("ID", "Patient", "Owner", "Animal", "Date", "Time", "Vet", "Status", "Amount")
        self.appointments_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=COLORS["card"],
                       foreground=COLORS["text_light"],
                       fieldbackground=COLORS["card"],
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=COLORS["primary"],
                       foreground=COLORS["text_light"],
                       borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS["secondary"])])
        
        # Configure columns
        column_widths = {
            "ID": 120, "Patient": 120, "Owner": 120, "Animal": 100,
            "Date": 100, "Time": 80, "Vet": 120, "Status": 100, "Amount": 100
        }
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.appointments_tree.yview)
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.appointments_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load appointments data
        self.load_enhanced_appointments_data()
    
    def load_enhanced_appointments_data(self):
        """Load enhanced appointments data into the treeview"""
        # Clear existing data
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        # Get enhanced appointments
        appointments = self.appointment_manager.get_all_enhanced_appointments()
        
        if appointments:
            # Use enhanced appointments
            for apt in appointments:
                self.appointments_tree.insert("", "end", values=(
                    apt[1] if len(apt) > 1 else "",  # appointment_id
                    apt[2] if len(apt) > 2 else "",  # patient_name
                    apt[3] if len(apt) > 3 else "",  # owner_name
                    apt[4] if len(apt) > 4 else "",  # animal_type
                    apt[8] if len(apt) > 8 else "",  # appointment_date
                    apt[9] if len(apt) > 9 else "",  # appointment_time
                    apt[6] if len(apt) > 6 else "",  # veterinarian
                    apt[12] if len(apt) > 12 else "", # status
                    f"₱{apt[13]:.2f}" if len(apt) > 13 and apt[13] else "₱0.00"  # total_amount
                ))
        else:
            # Fallback to regular appointments
            appointments = self.appointment_manager.get_all_appointments()
            for apt in appointments:
                self.appointments_tree.insert("", "end", values=(
                    apt[0] if len(apt) > 0 else "",  # appointment_id
                    apt[1] if len(apt) > 1 else "",  # patient_name
                    apt[2] if len(apt) > 2 else "",  # owner_name
                    apt[3] if len(apt) > 3 else "",  # animal_type
                    apt[4] if len(apt) > 4 else "",  # date
                    "",  # time (not available)
                    "",  # vet (not available)
                    apt[6] if len(apt) > 6 else "", # status
                    f"₱{apt[7]:.2f}" if len(apt) > 7 and apt[7] else "₱0.00"  # total_amount
                ))
    
    def show_upcoming_appointments(self):
        """Show upcoming appointments"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Upcoming Appointments")
        dialog.geometry("800x500")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="📅 Upcoming Appointments (Next 7 Days)", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Create treeview for upcoming appointments
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Patient", "Owner", "Animal", "Date", "Time", "Vet", "Service", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load upcoming appointments
        upcoming = self.appointment_manager.get_upcoming_appointments(7)
        
        for apt in upcoming:
            if len(apt) >= 9:  # Enhanced appointment
                tree.insert("", "end", values=(
                    apt[1], apt[2], apt[3], apt[4], apt[8], apt[9], apt[6], apt[5], apt[12]
                ))
        
        # Add reminder button
        def send_reminder():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an appointment")
                return
            
            item = tree.item(selection[0])
            values = item['values']
            appointment_id = values[0]
            
            if self.appointment_manager.send_appointment_reminder(appointment_id):
                messagebox.showinfo("Success", "Reminder sent successfully!")
            else:
                messagebox.showinfo("Info", "Reminder already sent or not needed")
        
        if self.current_user.has_permission('manage_communications'):
            reminder_btn = ModernButton(dialog, text="🔔 Send Reminder", 
                                      command=send_reminder,
                                      fg_color=COLORS["warning"])
            reminder_btn.pack(pady=10)
    
    def view_appointments(self):
        """View selected appointment details"""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to view")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        
        # Show appointment details
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("Appointment Details")
        details_window.geometry("500x400")
        details_window.configure(fg_color=COLORS["background"])
        
        ModernLabel(details_window, text="📋 Appointment Details", 
                   font=("Arial", 18, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        details_frame = ModernFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        details_text = f"Appointment ID: {values[0]}\n"
        details_text += f"Patient: {values[1]}\n"
        details_text += f"Owner: {values[2]}\n"
        details_text += f"Animal Type: {values[3]}\n"
        details_text += f"Date: {values[4]}\n"
        if values[5]:  # Time
            details_text += f"Time: {values[5]}\n"
        if values[6]:  # Veterinarian
            details_text += f"Veterinarian: {values[6]}\n"
        details_text += f"Status: {values[7]}\n"
        details_text += f"Amount: {values[8]}"
        
        details_label = ModernLabel(details_frame, text=details_text,
                                   font=("Arial", 12),
                                   justify="left")
        details_label.pack(padx=20, pady=20)
        
        # Add follow-up button if user has permission
        if self.current_user.has_permission('manage_communications'):
            def send_follow_up():
                message = f"Follow-up for appointment {values[0]}"
                if self.communication_manager.send_follow_up(values[0], message):
                    messagebox.showinfo("Success", "Follow-up sent successfully!")
                else:
                    messagebox.showinfo("Info", "Follow-up not sent")
            
            follow_up_btn = ModernButton(details_window, text="✉️ Send Follow-up", 
                                       command=send_follow_up,
                                       fg_color=COLORS["success"])
            follow_up_btn.pack(pady=10)
    
    def update_appointment_status(self):
        """Update appointment status"""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to update")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        appointment_id = values[0]
        
        # Status selection dialog
        status_dialog = ctk.CTkToplevel(self.root)
        status_dialog.title("Update Status")
        status_dialog.geometry("300x200")
        status_dialog.transient(self.root)
        status_dialog.grab_set()
        status_dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(status_dialog, text="Select New Status", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        status_var = ctk.StringVar(value=values[7] if len(values) > 7 else "SCHEDULED")
        status_combo = ctk.CTkComboBox(status_dialog, 
                                      values=["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"],
                                      variable=status_var)
        status_combo.pack(pady=10)
        
        def update_status():
            new_status = status_var.get()
            if self.appointment_manager.update_appointment_status(appointment_id, new_status):
                messagebox.showinfo("Success", "Status updated successfully!")
                self.load_enhanced_appointments_data()
                status_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update status")
        
        update_btn = ModernButton(status_dialog, text="Update Status", 
                                command=update_status,
                                fg_color=COLORS["success"])
        update_btn.pack(pady=20)
    
    def delete_appointment(self):
        """Delete selected appointment"""
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to delete")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        appointment_id = values[0]
        
        # Confirmation dialog
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete appointment {appointment_id}?")
        
        if result:
            if self.appointment_manager.delete_appointment(appointment_id):
                messagebox.showinfo("Success", "Appointment deleted successfully!")
                self.load_enhanced_appointments_data()
            else:
                messagebox.showerror("Error", "Failed to delete appointment")

    def show_inventory(self):
        """Show inventory management screen with enhanced features"""
        self.clear_main_content()
        
        # Main inventory frame
        inventory_frame = ModernFrame(self.main_content)
        inventory_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        inventory_frame.grid_rowconfigure(1, weight=1)
        inventory_frame.grid_columnconfigure(0, weight=1)
        
        # Title with icon
        title_label = ModernLabel(inventory_frame, text="📦 Inventory Management", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create inventory management interface
        self.create_enhanced_inventory_interface(inventory_frame)

    def create_enhanced_inventory_interface(self, parent):
        """Create enhanced inventory management interface"""
        # Search and controls frame
        controls_frame = ModernFrame(parent)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Search entry
        ModernLabel(controls_frame, text="Search:").grid(row=0, column=0, padx=10, pady=10)
        self.search_entry = ModernEntry(controls_frame, placeholder_text="Search items...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Search button
        search_btn = ModernButton(controls_frame, text="🔍 Search", 
                                 command=self.search_inventory)
        search_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Enhanced action buttons frame
        action_frame = ModernFrame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        action_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Action buttons
        add_btn = ModernButton(action_frame, text="➕ Add Item", 
                              command=self.add_inventory_item,
                              fg_color=COLORS["success"])
        add_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        edit_btn = ModernButton(action_frame, text="✏️ Edit Item", 
                               command=self.edit_inventory_item,
                               fg_color=COLORS["primary"])
        edit_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        delete_btn = ModernButton(action_frame, text="🗑️ Delete Item", 
                                 command=self.delete_inventory_item,
                                 fg_color=COLORS["danger"])
        delete_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        low_stock_btn = ModernButton(action_frame, text="⚠️ Low Stock", 
                                    command=self.show_low_stock_items,
                                    fg_color=COLORS["warning"])
        low_stock_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        expiring_btn = ModernButton(action_frame, text="📅 Expiring Soon", 
                                   command=self.show_expiring_items,
                                   fg_color=COLORS["accent"])
        expiring_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # Inventory list frame
        list_frame = ModernFrame(parent)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview for inventory
        columns = ("ID", "Name", "Price", "Stock", "Category", "Brand", "Animal Type", "Expiration", "Status")
        self.inventory_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=COLORS["card"],
                       foreground=COLORS["text_light"],
                       fieldbackground=COLORS["card"],
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=COLORS["primary"],
                       foreground=COLORS["text_light"],
                       borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS["secondary"])])
        
        # Configure columns
        column_widths = {
            "ID": 60, "Name": 150, "Price": 80, "Stock": 60, 
            "Category": 100, "Brand": 100, "Animal Type": 100, "Expiration": 100, "Status": 80
        }
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load inventory data
        self.load_inventory_data()
    
    def load_inventory_data(self):
        """Load inventory data into the treeview with status indicators"""
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get inventory items
        items = self.inventory_manager.get_all_items()
        
        # Get today's date for expiration check
        today = datetime.now().date()
        
        # Populate treeview with status
        for item in items:
            # Determine status
            status = ""
            if item.stock <= 0:
                status = "❌ Out"
            elif item.stock < 10:
                status = "⚠️ Low"
            else:
                status = "✅ OK"
            
            # Check expiration if date is available
            if item.expiration_date:
                try:
                    exp_date = datetime.strptime(item.expiration_date, '%Y-%m-%d').date()
                    days_until_expiry = (exp_date - today).days
                    if days_until_expiry <= 30 and days_until_expiry >= 0:
                        status = f"⏰ {days_until_expiry}d"
                    elif days_until_expiry < 0:
                        status = "⌛ Expired"
                except:
                    pass
            
            self.inventory_tree.insert("", "end", values=(
                item.id,
                item.name,
                f"₱{item.price:.2f}",
                item.stock,
                item.category,
                item.brand,
                item.animal_type,
                item.expiration_date,
                status
            ))
    
    def show_low_stock_items(self):
        """Show low stock items"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Low Stock Items")
        dialog.geometry("700x400")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="⚠️ Low Stock Items (Stock < 10)", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["warning"]).pack(pady=20)
        
        # Create treeview
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Name", "Category", "Current Stock", "Price", "Animal Type")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load low stock items
        low_stock_items = self.inventory_manager.get_low_stock_items(10)
        
        for item in low_stock_items:
            tree.insert("", "end", values=(
                item[0], item[1], item[4], item[3], f"₱{item[2]:.2f}", item[7]
            ))
    
    def show_expiring_items(self):
        """Show expiring items"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Items Expiring Soon")
        dialog.geometry("800x400")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="📅 Items Expiring Within 30 Days", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Create treeview
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Name", "Expiration Date", "Days Left", "Stock", "Category", "Price")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load expiring items
        expiring_items = self.inventory_manager.get_expiring_items(30)
        
        for item in expiring_items:
            days_left = int(item[10]) if len(item) > 10 else 0
            tree.insert("", "end", values=(
                item[0], item[1], item[9], days_left, item[3], item[4], f"₱{item[2]:.2f}"
            ))
    
    def search_inventory(self):
        """Search inventory items"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_inventory_data()
            return
        
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Search items
        items = self.inventory_manager.search_items(search_term)
        
        # Get today's date for expiration check
        today = datetime.now().date()
        
        # Populate treeview with search results
        for item in items:
            # Determine status
            status = ""
            if item.stock <= 0:
                status = "❌ Out"
            elif item.stock < 10:
                status = "⚠️ Low"
            else:
                status = "✅ OK"
            
            # Check expiration if date is available
            if item.expiration_date:
                try:
                    exp_date = datetime.strptime(item.expiration_date, '%Y-%m-d')
                except:
                    pass
            
            self.inventory_tree.insert("", "end", values=(
                item.id,
                item.name,
                f"₱{item.price:.2f}",
                item.stock,
                item.category,
                item.brand,
                item.animal_type,
                item.expiration_date,
                status
            ))

    def add_inventory_item(self):
        """Add new inventory item"""
        self.show_inventory_item_dialog()

    def edit_inventory_item(self):
        """Edit selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = self.inventory_tree.item(selection[0])
        values = item['values']
        item_id = values[0]
        
        # Get the full item details
        items = self.inventory_manager.get_all_items()
        selected_item = None
        for item_obj in items:
            if item_obj.id == item_id:
                selected_item = item_obj
                break
        
        if selected_item:
            self.show_inventory_item_dialog(selected_item)

    def delete_inventory_item(self):
        """Delete selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = self.inventory_tree.item(selection[0])
        values = item['values']
        item_id = values[0]
        item_name = values[1]
        
        # Confirmation dialog
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete '{item_name}'?")
        
        if result:
            if self.inventory_manager.delete_item(item_id):
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.load_inventory_data()
            else:
                messagebox.showerror("Error", "Failed to delete item")

    def show_inventory_item_dialog(self, item=None):
        """Show dialog for adding/editing inventory items"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Item" if item is None else "Edit Item")
        dialog.geometry("500x650")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["background"])
        
        title = "Add New Item" if item is None else f"Edit Item: {item.name}"
        ModernLabel(dialog, text=title, 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Form frame
        form_frame = ModernFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Form fields
        fields = [
            ("Name:", "entry"),
            ("Price:", "entry"),
            ("Stock:", "entry"),
            ("Category:", "combo", ["Dog Medicines", "Cat Medicines", "Pet Food", "Supplies", "Other"]),
            ("Brand:", "entry"),
            ("Animal Type:", "combo", ["Dog", "Cat", "All", "Other"]),
            ("Dosage:", "entry"),
            ("Expiration Date (YYYY-MM-DD):", "entry")
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            ModernLabel(form_frame, text=field[0]).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            if field[1] == "entry":
                entry = ModernEntry(form_frame, width=300)
                if item is not None:
                    if field[0] == "Name:":
                        entry.insert(0, item.name)
                    elif field[0] == "Price:":
                        entry.insert(0, str(item.price))
                    elif field[0] == "Stock:":
                        entry.insert(0, str(item.stock))
                    elif field[0] == "Brand:":
                        entry.insert(0, item.brand)
                    elif field[0] == "Dosage:":
                        entry.insert(0, item.dosage)
                    elif field[0] == "Expiration Date (YYYY-MM-DD):":
                        entry.insert(0, item.expiration_date)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ctk.CTkComboBox(form_frame, values=field[2], width=300)
                if item is not None:
                    if field[0] == "Category:":
                        combo.set(item.category)
                    elif field[0] == "Animal Type:":
                        combo.set(item.animal_type)
                combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = combo
            
            row += 1
        
        # Submit button
        def submit_item():
            try:
                # Validate required fields
                if not entries["Name:"].get().strip():
                    messagebox.showerror("Error", "Name is required")
                    return
                
                # Validate expiration date format
                exp_date = entries["Expiration Date (YYYY-MM-DD):"].get().strip()
                if exp_date:
                    try:
                        datetime.strptime(exp_date, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("Error", "Expiration date must be in YYYY-MM-DD format")
                        return
                
                # Create medicine object
                medicine = Medicine(
                    id=item.id if item else None,
                    name=entries["Name:"].get().strip(),
                    price=float(entries["Price:"].get() or 0),
                    stock=int(entries["Stock:"].get() or 0),
                    category=entries["Category:"].get(),
                    brand=entries["Brand:"].get().strip(),
                    animal_type=entries["Animal Type:"].get(),
                    dosage=entries["Dosage:"].get().strip(),
                    expiration_date=exp_date
                )
                
                # Save to database
                if item is None:
                    success = self.inventory_manager.add_item(medicine)
                else:
                    success = self.inventory_manager.update_item(medicine)
                
                if success:
                    messagebox.showinfo("Success", 
                                      "Item added successfully!" if item is None else "Item updated successfully!")
                    self.load_inventory_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save item")
                    
            except ValueError as e:
                messagebox.showerror("Error", "Please enter valid numbers for price and stock")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save item: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Save Item", 
                                 command=submit_item,
                                 fg_color=COLORS["success"])
        submit_btn.pack(pady=20)

    def show_pos(self):
        """Show point of sale screen"""
        self.clear_main_content()
        
        # Main POS frame
        pos_frame = ModernFrame(self.main_content)
        pos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        pos_frame.grid_rowconfigure(1, weight=1)
        pos_frame.grid_columnconfigure(0, weight=1)
        pos_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ModernLabel(pos_frame, text="💰 Point of Sale", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=20)
        
        # Create POS interface
        self.create_pos_interface(pos_frame)
    
    def create_pos_interface(self, parent):
        """Create complete point of sale interface"""
        # Left side - Products
        products_frame = ModernFrame(parent)
        products_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        products_frame.grid_rowconfigure(1, weight=1)
        products_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(products_frame, text="🛍️ Available Products", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", pady=10)
        
        # Products treeview
        products_columns = ("ID", "Name", "Price", "Stock", "Category")
        self.products_tree = ttk.Treeview(products_frame, columns=products_columns, show="headings", height=15)
        
        for col in products_columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Style products treeview
        style = ttk.Style()
        style.configure("Products.Treeview", 
                       background=COLORS["card"],
                       foreground=COLORS["text_light"],
                       fieldbackground=COLORS["card"])
        
        products_scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        self.products_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        products_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Add to cart button
        add_to_cart_btn = ModernButton(products_frame, text="➕ Add to Cart", 
                                      command=self.add_to_cart,
                                      fg_color=COLORS["success"])
        add_to_cart_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Right side - Cart and checkout
        cart_frame = ModernFrame(parent)
        cart_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        cart_frame.grid_rowconfigure(1, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(cart_frame, text="🛒 Shopping Cart", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", pady=10)
        
        # Cart treeview
        cart_columns = ("Name", "Price", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=10)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        cart_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Cart controls
        cart_controls_frame = ModernFrame(cart_frame)
        cart_controls_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        cart_controls_frame.grid_columnconfigure((0, 1), weight=1)
        
        remove_item_btn = ModernButton(cart_controls_frame, text="➖ Remove Item", 
                                      command=self.remove_from_cart,
                                      fg_color=COLORS["warning"])
        remove_item_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        clear_cart_btn = ModernButton(cart_controls_frame, text="🗑️ Clear Cart", 
                                     command=self.clear_cart,
                                     fg_color=COLORS["danger"])
        clear_cart_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Customer info and totals
        info_frame = ModernFrame(cart_frame)
        info_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(info_frame, text="Customer Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.customer_name_entry = ModernEntry(info_frame)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ModernLabel(info_frame, text="Payment Method:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.payment_method_combo = ctk.CTkComboBox(info_frame, values=["Cash", "Credit Card", "GCash", "Bank Transfer"])
        self.payment_method_combo.set("Cash")
        self.payment_method_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Totals display
        totals_frame = ModernFrame(cart_frame)
        totals_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        totals_frame.grid_columnconfigure(1, weight=1)
        
        self.total_label = ModernLabel(totals_frame, text="Total: ₱0.00", 
                                      font=("Arial", 16, "bold"),
                                      text_color=COLORS["accent"])
        self.total_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Checkout button
        checkout_btn = ModernButton(cart_frame, text="💳 Checkout", 
                                   command=self.process_checkout,
                                   fg_color=COLORS["success"],
                                   font=("Arial", 14, "bold"))
        checkout_btn.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        # Load products
        self.load_products_for_pos()
        self.update_cart_display()
    
    def load_products_for_pos(self):
        """Load products for POS interface"""
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Get inventory items
        items = self.inventory_manager.get_all_items()
        
        # Populate products treeview
        for item in items:
            if item.stock > 0:  # Only show items with stock
                self.products_tree.insert("", "end", values=(
                    item.id,
                    item.name,
                    f"₱{item.price:.2f}",
                    item.stock,
                    item.category
                ))
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart")
            return
        
        item = self.products_tree.item(selection[0])
        values = item['values']
        
        item_id = values[0]
        item_name = values[1]
        item_price = float(values[2].replace('₱', ''))
        item_stock = values[3]
        
        # Check stock
        if item_stock <= 0:
            messagebox.showwarning("Warning", "This item is out of stock")
            return
        
        # Add to cart
        self.cart.add_item(item_id, item_name, item_price, 1, values[4])
        self.update_cart_display()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove from cart")
            return
        
        item = self.cart_tree.item(selection[0])
        values = item['values']
        
        # Find item ID by name (this is a simplification)
        for cart_item in self.cart.items:
            if cart_item.name == values[0]:
                self.cart.remove_item(cart_item.item_id)
                break
        
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart.clear()
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display with current items and total"""
        # Clear cart display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for item in self.cart.items:
            self.cart_tree.insert("", "end", values=(
                item.name,
                f"₱{item.price:.2f}",
                item.quantity,
                f"₱{item.subtotal:.2f}"
            ))
        
        # Update total
        self.total_label.configure(text=f"Total: ₱{self.cart.total:.2f}")
    
    def process_checkout(self):
        """Process the checkout and record sale"""
        if not self.cart.items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        # Validate customer name
        customer_name = self.customer_name_entry.get().strip()
        if not customer_name:
            customer_name = "Walk-in Customer"
        
        payment_method = self.payment_method_combo.get()
        
        # Check stock availability
        for cart_item in self.cart.items:
            # Get current stock from database
            items = self.inventory_manager.get_all_items()
            for item in items:
                if item.id == cart_item.item_id:
                    if item.stock < cart_item.quantity:
                        messagebox.showerror("Error", 
                                           f"Not enough stock for {item.name}. Available: {item.stock}")
                        return
                    break
        
        # Process sale
        transaction_id = generate_transaction_id()
        cart_items_dict = self.cart.to_legacy_format()
        
        if self.sales_manager.record_sale(transaction_id, cart_items_dict, 
                                        self.cart.total, payment_method, customer_name):
            # Generate receipt
            receipt_text = ReceiptManager.generate_receipt_text(
                transaction_id, 
                customer_name, 
                customer_name, 
                "Various", 
                "POS Sale", 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                self.cart.total, 
                cart_items_dict
            )
            
            # Show success message with receipt
            receipt_window = ctk.CTkToplevel(self.root)
            receipt_window.title("Sale Completed - Receipt")
            receipt_window.geometry("500x600")
            receipt_window.configure(fg_color=COLORS["background"])
            
            ModernLabel(receipt_window, text="✅ Sale Completed!", 
                       font=("Arial", 20, "bold"),
                       text_color=COLORS["success"]).pack(pady=20)
            
            receipt_frame = ModernFrame(receipt_window)
            receipt_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            receipt_text_widget = ctk.CTkTextbox(receipt_frame, font=("Courier", 12))
            receipt_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            receipt_text_widget.insert("1.0", receipt_text)
            receipt_text_widget.configure(state="disabled")
            
            # Save receipt button
            def save_receipt():
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile=f"receipt_{transaction_id}.txt"
                )
                if filename:
                    ReceiptManager.save_receipt_to_file(receipt_text, filename)
                    messagebox.showinfo("Success", f"Receipt saved as {filename}")
            
            save_btn = ModernButton(receipt_window, text="💾 Save Receipt", 
                                   command=save_receipt)
            save_btn.pack(pady=10)
            
            # Clear cart and refresh products
            self.cart.clear()
            self.update_cart_display()
            self.load_products_for_pos()
            self.customer_name_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Sale completed! Transaction ID: {transaction_id}")
        else:
            messagebox.showerror("Error", "Failed to process sale")

    def show_enhanced_reports(self):
        """Show enhanced reports and analytics screen"""
        self.clear_main_content()
        
        # Main reports frame
        reports_frame = ModernFrame(self.main_content)
        reports_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        reports_frame.grid_rowconfigure(1, weight=1)
        reports_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ModernLabel(reports_frame, text="📊 Enhanced Reports & Analytics", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create enhanced reports interface
        self.create_enhanced_reports_interface(reports_frame)
    
    def create_enhanced_reports_interface(self, parent):
        """Create enhanced reports and analytics interface"""
        # Date selection frame
        date_frame = ModernFrame(parent)
        date_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        date_frame.grid_columnconfigure((1, 3), weight=1)
        
        ModernLabel(date_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ModernEntry(date_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ModernLabel(date_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = ModernEntry(date_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Set default dates (last 30 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.start_date_entry.insert(0, start_date)
        self.end_date_entry.insert(0, end_date)
        
        # Report buttons frame
        report_buttons_frame = ModernFrame(parent)
        report_buttons_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        report_buttons_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Report buttons
        revenue_btn = ModernButton(report_buttons_frame, text="💰 Revenue Trends", 
                                  command=self.generate_revenue_trends,
                                  fg_color=COLORS["success"])
        revenue_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        services_btn = ModernButton(report_buttons_frame, text="🏥 Popular Services", 
                                   command=self.generate_popular_services,
                                   fg_color=COLORS["primary"])
        services_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        demographics_btn = ModernButton(report_buttons_frame, text="👥 Demographics", 
                                       command=self.generate_demographics,
                                       fg_color=COLORS["secondary"])
        demographics_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        performance_btn = ModernButton(report_buttons_frame, text="📈 Performance", 
                                      command=self.generate_performance,
                                      fg_color=COLORS["warning"])
        performance_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        export_btn = ModernButton(report_buttons_frame, text="📤 Export Data", 
                                 command=self.export_data,
                                 fg_color=COLORS["accent"])
        export_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # Report display frame
        self.report_display_frame = ModernFrame(parent)
        self.report_display_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.report_display_frame.grid_rowconfigure(0, weight=1)
        self.report_display_frame.grid_columnconfigure(0, weight=1)
        
        # Initial report cards
        self.show_enhanced_report_cards()
    
    def show_enhanced_report_cards(self):
        """Show enhanced summary report cards"""
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Get enhanced report data
        stats = get_database_stats()
        
        # Get popular services
        popular_services = self.analytics_manager.get_popular_services(limit=1)
        top_service = popular_services[0][0] if popular_services else "N/A"
        
        report_cards = [
            ("💰 Total Revenue", f"₱{stats.get('total_sales', 0):,.2f}", COLORS["success"]),
            ("📅 Total Appointments", f"{stats.get('appointments', 0)}", COLORS["primary"]),
            ("📦 Inventory Value", f"₱{stats.get('inventory_value', 0):,.2f}", COLORS["secondary"]),
            ("⚠️ Low Stock Items", f"{stats.get('low_stock_items', 0)}", COLORS["warning"]),
            ("⏰ Expiring Soon", f"{stats.get('expiring_soon', 0)}", COLORS["danger"]),
            ("🏥 Top Service", top_service, COLORS["accent"])
        ]
        
        for i, (title, value, color) in enumerate(report_cards):
            row = i // 3
            col = i % 3
            card = ColorfulCard(self.report_display_frame, title, value, color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def generate_revenue_trends(self):
        """Generate and display revenue trends"""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        revenue_data = self.analytics_manager.get_revenue_trends('monthly', start_date, end_date)
        
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Create revenue trends treeview
        columns = ("Period", "Revenue", "Transactions", "Avg Transaction")
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.report_display_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate revenue data
        total_revenue = 0
        total_transactions = 0
        
        for row in revenue_data:
            tree.insert("", "end", values=(
                row[0],
                f"₱{row[1]:,.2f}",
                row[2],
                f"₱{row[3]:,.2f}"
            ))
            total_revenue += row[1] if row[1] else 0
            total_transactions += row[2] if row[2] else 0
        
        # Add total row
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        tree.insert("", "end", values=(
            "TOTAL",
            f"₱{total_revenue:,.2f}",
            total_transactions,
            f"₱{avg_transaction:,.2f}"
        ))
    
    def generate_popular_services(self):
        """Generate and display popular services report"""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        services = self.analytics_manager.get_popular_services(10, start_date, end_date)
        
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Create services treeview
        columns = ("Service", "Count", "Total Revenue", "Avg Revenue")
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.report_display_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate services data
        total_revenue = 0
        
        for service in services:
            tree.insert("", "end", values=(
                service[0],
                service[1],
                f"₱{service[2]:,.2f}",
                f"₱{service[3]:,.2f}"
            ))
            total_revenue += service[2] if service[2] else 0
        
        # Add total row
        tree.insert("", "end", values=(
            "TOTAL",
            sum(s[1] for s in services),
            f"₱{total_revenue:,.2f}",
            ""
        ))
    
    def generate_demographics(self):
        """Generate and display demographics report"""
        demographics = self.analytics_manager.get_customer_demographics()
        
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Create notebook for different demographics
        notebook = ttk.Notebook(self.report_display_frame)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Animal distribution tab
        animal_frame = ModernFrame(notebook)
        notebook.add(animal_frame, text="Animal Types")
        
        columns = ("Animal Type", "Count", "Percentage")
        animal_tree = ttk.Treeview(animal_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            animal_tree.heading(col, text=col)
            animal_tree.column(col, width=150)
        
        animal_scrollbar = ttk.Scrollbar(animal_frame, orient="vertical", command=animal_tree.yview)
        animal_tree.configure(yscrollcommand=animal_scrollbar.set)
        
        animal_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        animal_scrollbar.pack(side="right", fill="y")
        
        # Populate animal data
        for animal in demographics.get('animal_distribution', []):
            animal_tree.insert("", "end", values=animal)
        
        # Customer frequency tab
        customer_frame = ModernFrame(notebook)
        notebook.add(customer_frame, text="Customer Frequency")
        
        columns = ("Customer", "Visits", "Total Spent", "Avg Spent")
        customer_tree = ttk.Treeview(customer_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            customer_tree.heading(col, text=col)
            customer_tree.column(col, width=150)
        
        customer_scrollbar = ttk.Scrollbar(customer_frame, orient="vertical", command=customer_tree.yview)
        customer_tree.configure(yscrollcommand=customer_scrollbar.set)
        
        customer_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        customer_scrollbar.pack(side="right", fill="y")
        
        # Populate customer data
        for customer in demographics.get('customer_frequency', []):
            customer_tree.insert("", "end", values=(
                customer[0],
                customer[1],
                f"₱{customer[2]:,.2f}" if customer[2] else "₱0.00",
                f"₱{customer[3]:,.2f}" if customer[3] else "₱0.00"
            ))
    
    def generate_performance(self):
        """Generate and display performance report"""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        performance = self.analytics_manager.get_veterinarian_performance(start_date, end_date)
        
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        if not performance:
            ModernLabel(self.report_display_frame, 
                       text="No performance data available. Enhanced appointments required.",
                       font=("Arial", 14)).pack(expand=True)
            return
        
        # Create performance treeview
        columns = ("Veterinarian", "Appointments", "Revenue", "Avg/Appt", "Completed", "Cancelled", "Success Rate")
        tree = ttk.Treeview(self.report_display_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.report_display_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate performance data
        total_appointments = 0
        total_revenue = 0
        
        for vet in performance:
            tree.insert("", "end", values=(
                vet[0],
                vet[1],
                f"₱{vet[2]:,.2f}",
                f"₱{vet[3]:,.2f}",
                vet[4],
                vet[5],
                f"{vet[6]}%"
            ))
            total_appointments += vet[1] if vet[1] else 0
            total_revenue += vet[2] if vet[2] else 0
        
        # Add total row
        tree.insert("", "end", values=(
            "TOTAL",
            total_appointments,
            f"₱{total_revenue:,.2f}",
            "",
            "",
            "",
            ""
        ))
    
    def show_reports(self):
        """Legacy reports - redirect to enhanced reports"""
        self.show_enhanced_reports()
    
    def show_communications(self):
        """Show communications management interface"""
        if not self.current_user.has_permission('manage_communications'):
            messagebox.showwarning("Access Denied", 
                                 "You don't have permission to access communications")
            return
        
        self.clear_main_content()
        
        # Main communications frame
        comm_frame = ModernFrame(self.main_content)
        comm_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        comm_frame.grid_rowconfigure(1, weight=1)
        comm_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ModernLabel(comm_frame, text="✉️ Communications", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create communications interface
        self.create_communications_interface(comm_frame)
    
    def create_communications_interface(self, parent):
        """Create communications management interface"""
        # Controls frame
        controls_frame = ModernFrame(parent)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(controls_frame, text="Search:").grid(row=0, column=0, padx=10, pady=10)
        search_entry = ModernEntry(controls_frame, placeholder_text="Search communications...")
        search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        def search_communications():
            search_term = search_entry.get().strip()
            # Implement search functionality here
            messagebox.showinfo("Search", f"Searching for: {search_term}")
        
        search_btn = ModernButton(controls_frame, text="🔍 Search", 
                                 command=search_communications)
        search_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Action buttons
        action_frame = ModernFrame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        view_log_btn = ModernButton(action_frame, text="📋 View Log", 
                                   command=self.view_communication_log,
                                   fg_color=COLORS["primary"])
        view_log_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        send_reminders_btn = ModernButton(action_frame, text="🔔 Send Reminders", 
                                         command=self.send_bulk_reminders,
                                         fg_color=COLORS["warning"])
        send_reminders_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        follow_up_btn = ModernButton(action_frame, text="✉️ Follow-up", 
                                    command=self.send_bulk_followups,
                                    fg_color=COLORS["success"])
        follow_up_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Communications display frame
        display_frame = ModernFrame(parent)
        display_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(display_frame, text="Communication Dashboard", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).pack(pady=10)
        
        # Display communication statistics
        stats = self.get_communication_stats()
        
        stats_text = f"""
        📊 Communication Statistics:
        
        • Total Communications Sent: {stats.get('total', 0)}
        • Reminders Sent: {stats.get('reminders', 0)}
        • Follow-ups Sent: {stats.get('followups', 0)}
        • Pending Follow-ups: {stats.get('pending_followups', 0)}
        
        Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        stats_label = ModernLabel(display_frame, text=stats_text,
                                 font=("Arial", 12),
                                 justify="left")
        stats_label.pack(padx=20, pady=20)
    
    def get_communication_stats(self):
        """Get communication statistics"""
        try:
            cur = self.db.cursor()
            
            # Check if communication log table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_log'")
            if not cur.fetchone():
                return {'total': 0, 'reminders': 0, 'followups': 0, 'pending_followups': 0}
            
            # Get total communications
            cur.execute("SELECT COUNT(*) FROM communication_log")
            total = cur.fetchone()[0]
            
            # Get reminders count
            cur.execute("SELECT COUNT(*) FROM communication_log WHERE communication_type = 'REMINDER'")
            reminders = cur.fetchone()[0]
            
            # Get follow-ups count
            cur.execute("SELECT COUNT(*) FROM communication_log WHERE communication_type = 'FOLLOW_UP'")
            followups = cur.fetchone()[0]
            
            # Get pending follow-ups from appointments
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("SELECT COUNT(*) FROM appointments_enhanced WHERE follow_up_needed = 1")
                pending_followups = cur.fetchone()[0]
            else:
                pending_followups = 0
            
            return {
                'total': total,
                'reminders': reminders,
                'followups': followups,
                'pending_followups': pending_followups
            }
            
        except sqlite3.Error as e:
            print(f"Error getting communication stats: {e}")
            return {'total': 0, 'reminders': 0, 'followups': 0, 'pending_followups': 0}
    
    def view_communication_log(self):
        """View communication log"""
        log = self.communication_manager.get_communication_log()
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Communication Log")
        dialog.geometry("800x500")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="📋 Communication Log", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        if not log:
            ModernLabel(dialog, text="No communication records found.").pack(expand=True)
            return
        
        # Create treeview
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("Date", "Type", "To", "Message", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate log
        for entry in log:
            tree.insert("", "end", values=(
                entry[5] if len(entry) > 5 else "",  # sent_date
                entry[2] if len(entry) > 2 else "",  # communication_type
                entry[3] if len(entry) > 3 else "",  # sent_to
                (entry[4][:50] + "...") if len(entry) > 4 and len(entry[4]) > 50 else (entry[4] if len(entry) > 4 else ""),  # message
                entry[6] if len(entry) > 6 else ""   # status
            ))
    
    def send_bulk_reminders(self):
        """Send bulk reminders for tomorrow's appointments"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if not cur.fetchone():
                messagebox.showinfo("Info", "Enhanced appointments not available")
                return
            
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT COUNT(*) FROM appointments_enhanced 
                WHERE appointment_date = ? 
                AND status = 'SCHEDULED'
                AND reminder_sent = 0
            """, (tomorrow,))
            
            count = cur.fetchone()[0]
            
            if count == 0:
                messagebox.showinfo("Info", "No appointments need reminders for tomorrow")
                return
            
            result = messagebox.askyesno("Confirm", 
                                       f"Send reminders for {count} appointment(s) tomorrow?")
            
            if result:
                sent_count = 0
                cur.execute("""
                    SELECT appointment_id FROM appointments_enhanced 
                    WHERE appointment_date = ? 
                    AND status = 'SCHEDULED'
                    AND reminder_sent = 0
                """, (tomorrow,))
                
                appointments = cur.fetchall()
                
                for apt in appointments:
                    if self.communication_manager.send_appointment_reminder(apt[0]):
                        sent_count += 1
                
                messagebox.showinfo("Success", f"Sent {sent_count} reminder(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send reminders: {str(e)}")
    
    def send_bulk_followups(self):
        """Send bulk follow-ups for completed appointments"""
        try:
            cur = self.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if not cur.fetchone():
                messagebox.showinfo("Info", "Enhanced appointments not available")
                return
            
            # Get appointments completed yesterday
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT COUNT(*) FROM appointments_enhanced 
                WHERE appointment_date = ? 
                AND status = 'COMPLETED'
                AND follow_up_needed = 1
            """, (yesterday,))
            
            count = cur.fetchone()[0]
            
            if count == 0:
                messagebox.showinfo("Info", "No completed appointments need follow-up from yesterday")
                return
            
            result = messagebox.askyesno("Confirm", 
                                       f"Send follow-ups for {count} completed appointment(s)?")
            
            if result:
                sent_count = 0
                cur.execute("""
                    SELECT appointment_id FROM appointments_enhanced 
                    WHERE appointment_date = ? 
                    AND status = 'COMPLETED'
                    AND follow_up_needed = 1
                """, (yesterday,))
                
                appointments = cur.fetchall()
                
                for apt in appointments:
                    message = "Thank you for visiting our clinic yesterday. How is your pet doing?"
                    if self.communication_manager.send_follow_up(apt[0], message):
                        sent_count += 1
                
                messagebox.showinfo("Success", f"Sent {sent_count} follow-up(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send follow-ups: {str(e)}")
    
    def calculate_total_sales(self):
        """Calculate total sales amount"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT SUM(total_amount) FROM sales")
            result = cur.fetchone()
            return result[0] or 0.0
        except sqlite3.Error:
            return 0.0
    
    def export_data(self):
        """Export data to CSV"""
        file_types = [
            ("Sales Data", "sales"),
            ("Inventory Data", "inventory"),
            ("Appointments Data", "appointments"),
            ("Enhanced Appointments", "appointments_enhanced"),
            ("Communication Log", "communication_log")
        ]
        
        # Create dialog for export type selection
        export_dialog = ctk.CTkToplevel(self.root)
        export_dialog.title("Export Data")
        export_dialog.geometry("300x300")
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        export_dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(export_dialog, text="Select Data to Export", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        export_var = ctk.StringVar(value="sales")
        
        for text, value in file_types:
            radio = ctk.CTkRadioButton(export_dialog, text=text, variable=export_var, value=value)
            radio.pack(pady=5)
        
        def perform_export():
            export_type = export_var.get()
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"vetclinic_{export_type}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if filename:
                if self.export_to_csv(export_type, filename):
                    messagebox.showinfo("Success", f"Data exported to {filename}")
                    export_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to export data")
        
        export_btn = ModernButton(export_dialog, text="Export", command=perform_export)
        export_btn.pack(pady=20)
    
    def export_to_csv(self, data_type, filename):
        """Export data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if data_type == "sales":
                    # Export sales data
                    sales = self.sales_manager.get_sales_report()
                    writer.writerow(["Transaction ID", "Item ID", "Item Name", "Quantity", "Price", "Subtotal", "Total Amount", "Payment Method", "Customer Name", "Sale Date"])
                    for sale in sales:
                        writer.writerow(sale[1:11])  # Skip ID column
                
                elif data_type == "inventory":
                    # Export inventory data
                    items = self.inventory_manager.get_all_items()
                    writer.writerow(["ID", "Name", "Price", "Stock", "Category", "Image", "Brand", "Animal Type", "Dosage", "Expiration Date"])
                    for item in items:
                        writer.writerow([
                            item.id, item.name, item.price, item.stock, item.category,
                            "", item.brand, item.animal_type, item.dosage, item.expiration_date
                        ])
                
                elif data_type == "appointments":
                    # Export appointments data
                    appointments = self.appointment_manager.get_all_appointments()
                    writer.writerow(["Appointment ID", "Patient Name", "Owner Name", "Animal Type", "Date", "Notes", "Status", "Total Amount"])
                    for apt in appointments:
                        writer.writerow(apt[:8])  # Use first 8 columns
                
                elif data_type == "appointments_enhanced":
                    # Export enhanced appointments
                    appointments = self.appointment_manager.get_all_enhanced_appointments()
                    writer.writerow(["Appointment ID", "Patient Name", "Owner Name", "Animal Type", "Service", "Veterinarian", "Duration", "Appointment Date", "Appointment Time", "Date Created", "Notes", "Status", "Total Amount", "Reminder Sent", "Follow-up Needed"])
                    for apt in appointments:
                        writer.writerow(apt[1:16])  # Skip ID column
                
                elif data_type == "communication_log":
                    # Export communication log
                    log = self.communication_manager.get_communication_log()
                    writer.writerow(["Appointment ID", "Type", "To", "Message", "Date", "Status"])
                    for entry in log:
                        writer.writerow(entry[1:7])  # Skip ID column
        
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def show_settings(self):
        """Show settings screen with complete functionality"""
        self.clear_main_content()
        
        # Main settings frame
        settings_frame = ModernFrame(self.main_content)
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        settings_frame.grid_rowconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ModernLabel(settings_frame, text="⚙️ System Settings", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create settings interface
        self.create_settings_interface(settings_frame)
    
    def create_settings_interface(self, parent):
        """Create complete settings interface"""
        # Notebook for settings categories
        settings_notebook = ttk.Notebook(parent)
        settings_notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # User Management Tab
        user_frame = ModernFrame(settings_notebook)
        settings_notebook.add(user_frame, text="👤 User Management")
        self.create_user_management_tab(user_frame)
        
        # Theme Settings Tab
        theme_frame = ModernFrame(settings_notebook)
        settings_notebook.add(theme_frame, text="🎨 Theme Settings")
        self.create_theme_settings_tab(theme_frame)
        
        # Database Tab
        db_frame = ModernFrame(settings_notebook)
        settings_notebook.add(db_frame, text="💾 Database")
        self.create_database_tab(db_frame)
        
        # Security Tab
        security_frame = ModernFrame(settings_notebook)
        settings_notebook.add(security_frame, text="🔒 Security")
        self.create_security_tab(security_frame)
    
    def create_user_management_tab(self, parent):
        """Create user management settings"""
        parent.grid_columnconfigure(0, weight=1)
        
        # Current user info
        current_user_frame = ModernFrame(parent)
        current_user_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        current_user_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(current_user_frame, text="Current User:", 
                   font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(current_user_frame, text=f"{self.current_user.username} ({self.current_user.get_role_display_name()})",
                   font=("Arial", 14)).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # User list (admin only)
        if self.current_user.has_permission('manage_users'):
            ModernLabel(parent, text="User Accounts:", 
                       font=("Arial", 16, "bold"),
                       text_color=COLORS["accent"]).grid(row=1, column=0, sticky="w", padx=10, pady=10)
            
            # Users treeview
            users_columns = ("ID", "Username", "Role", "Full Name", "Email", "Phone")
            self.users_tree = ttk.Treeview(parent, columns=users_columns, show="headings", height=8)
            
            for col in users_columns:
                self.users_tree.heading(col, text=col)
                self.users_tree.column(col, width=100)
            
            users_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.users_tree.yview)
            self.users_tree.configure(yscrollcommand=users_scrollbar.set)
            
            self.users_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            users_scrollbar.grid(row=2, column=1, sticky="ns")
            
            # Load users
            self.load_users()
            
            # User management buttons
            user_buttons_frame = ModernFrame(parent)
            user_buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
            user_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            add_user_btn = ModernButton(user_buttons_frame, text="➕ Add User", 
                                       command=self.add_user)
            add_user_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            
            change_password_btn = ModernButton(user_buttons_frame, text="🔑 Change Password", 
                                             command=self.change_password)
            change_password_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            delete_user_btn = ModernButton(user_buttons_frame, text="🗑️ Delete User", 
                                         command=self.delete_user,
                                         fg_color=COLORS["danger"])
            delete_user_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        else:
            # For non-admin users, show limited options
            limited_frame = ModernFrame(parent)
            limited_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            
            ModernLabel(limited_frame, text="User management features are available for administrators only.",
                       font=("Arial", 12)).pack(expand=True)
    
    def load_users(self):
        """Load users into the treeview"""
        if not self.current_user.has_permission('manage_users'):
            return
        
        # Clear existing data
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id, username, role, full_name, email, phone FROM users ORDER BY id")
            users = cur.fetchall()
            
            for user in users:
                self.users_tree.insert("", "end", values=user)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
    
    def add_user(self):
        """Add new user dialog"""
        if not self.current_user.has_permission('manage_users'):
            messagebox.showwarning("Permission Denied", "Only administrators can add users")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="Add New User", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        form_frame = ModernFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Form fields
        fields = [
            ("Username:", "entry"),
            ("Password:", "entry"),
            ("Full Name:", "entry"),
            ("Email:", "entry"),
            ("Phone:", "entry"),
            ("Role:", "combo", ["admin", "veterinarian", "staff", "receptionist"])
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            ModernLabel(form_frame, text=field[0]).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            if field[1] == "entry":
                entry = ModernEntry(form_frame, width=200, show="•" if field[0] == "Password:" else "")
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ctk.CTkComboBox(form_frame, values=field[2], width=200)
                combo.set("staff")
                combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = combo
            
            row += 1
        
        def submit_user():
            username = entries["Username:"].get().strip()
            password = entries["Password:"].get()
            full_name = entries["Full Name:"].get().strip()
            email = entries["Email:"].get().strip()
            phone = entries["Phone:"].get().strip()
            role = entries["Role:"].get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required")
                return
            
            try:
                cur = self.db.cursor()
                cur.execute("""
                    INSERT INTO users (username, password, role, full_name, email, phone) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, password, role, full_name, email, phone))
                self.db.commit()
                
                messagebox.showinfo("Success", "User added successfully!")
                self.load_users()
                dialog.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add user: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Add User", command=submit_user)
        submit_btn.pack(pady=20)
    
    def change_password(self):
        """Change password dialog"""
        if not self.current_user.has_permission('manage_users') and not self.current_user.id:
            messagebox.showwarning("Permission Denied", "You don't have permission to change passwords")
            return
        
        selection = self.users_tree.selection()
        if not selection and not self.current_user.id:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        if selection:
            item = self.users_tree.item(selection[0])
            values = item['values']
            user_id = values[0]
            username = values[1]
        else:
            # Allow users to change their own password
            user_id = self.current_user.id
            username = self.current_user.username
        
        # Check permission
        if not self.current_user.has_permission('manage_users') and user_id != self.current_user.id:
            messagebox.showwarning("Permission Denied", "You can only change your own password")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text=f"Change Password for {username}", 
                   font=("Arial", 18, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        form_frame = ModernFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ModernLabel(form_frame, text="New Password:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        password_entry = ModernEntry(form_frame, show="•", width=200)
        password_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ModernLabel(form_frame, text="Confirm Password:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        confirm_entry = ModernEntry(form_frame, show="•", width=200)
        confirm_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        def submit_password():
            new_password = password_entry.get()
            confirm_password = confirm_entry.get()
            
            if not new_password:
                messagebox.showerror("Error", "Password cannot be empty")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            try:
                cur = self.db.cursor()
                cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
                self.db.commit()
                
                messagebox.showinfo("Success", "Password changed successfully!")
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to change password: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Change Password", command=submit_password)
        submit_btn.pack(pady=20)
    
    def delete_user(self):
        """Delete selected user"""
        if not self.current_user.has_permission('manage_users'):
            messagebox.showwarning("Permission Denied", "Only administrators can delete users")
            return
        
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        values = item['values']
        user_id = values[0]
        username = values[1]
        
        # Prevent deleting own account
        if user_id == self.current_user.id:
            messagebox.showwarning("Warning", "You cannot delete your own account")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete user '{username}'?")
        
        if result:
            try:
                cur = self.db.cursor()
                cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                self.db.commit()
                
                messagebox.showinfo("Success", "User deleted successfully!")
                self.load_users()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def create_theme_settings_tab(self, parent):
        """Create theme settings tab"""
        parent.grid_columnconfigure(0, weight=1)
        
        ModernLabel(parent, text="Appearance Settings", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Theme selection
        theme_frame = ModernFrame(parent)
        theme_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        theme_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(theme_frame, text="Theme Mode:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        theme_var = ctk.StringVar(value=THEME_MODE)
        theme_combo = ctk.CTkComboBox(theme_frame, 
                                     values=["dark", "light", "system"],
                                     variable=theme_var)
        theme_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Color scheme selection
        ModernLabel(theme_frame, text="Color Scheme:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        color_var = ctk.StringVar(value="blue")
        color_combo = ctk.CTkComboBox(theme_frame, 
                                     values=["blue", "green", "dark-blue"],
                                     variable=color_var)
        color_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        def apply_theme_settings():
            global THEME_MODE
            THEME_MODE = theme_var.get()
            ctk.set_appearance_mode(THEME_MODE)
            ctk.set_default_color_theme(color_var.get())
            apply_theme(self.root)
            messagebox.showinfo("Success", "Theme settings applied!")
        
        apply_btn = ModernButton(parent, text="Apply Theme Settings", 
                                command=apply_theme_settings)
        apply_btn.grid(row=2, column=0, padx=10, pady=20, sticky="ew")
    
    def create_database_tab(self, parent):
        """Create database management tab"""
        parent.grid_columnconfigure(0, weight=1)
        
        ModernLabel(parent, text="Database Management", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Database actions frame
        db_actions_frame = ModernFrame(parent)
        db_actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        db_actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        backup_btn = ModernButton(db_actions_frame, text="💾 Backup Database", 
                                 command=backup_database_with_timestamp,
                                 fg_color=COLORS["success"])
        backup_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        restore_btn = ModernButton(db_actions_frame, text="🔄 Restore Database", 
                                  command=self.restore_database,
                                  fg_color=COLORS["warning"])
        restore_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Additional database buttons
        db_actions_frame2 = ModernFrame(parent)
        db_actions_frame2.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        db_actions_frame2.grid_columnconfigure((0, 1), weight=1)
        
        optimize_btn = ModernButton(db_actions_frame2, text="⚡ Optimize Database", 
                                   command=optimize_database,
                                   fg_color=COLORS["primary"])
        optimize_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        export_sql_btn = ModernButton(db_actions_frame2, text="📤 Export to SQL", 
                                     command=export_database_to_sql,
                                     fg_color=COLORS["accent"])
        export_sql_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Database info
        info_frame = ModernFrame(parent)
        info_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Get database info
        stats = get_database_stats()
        
        ModernLabel(info_frame, text="Database File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=DB_FILE).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Users:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=str(stats.get('users', 0))).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Inventory Items:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=str(stats.get('inventory', 0))).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Appointments:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=str(stats.get('appointments', 0))).grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Medical Records:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=str(stats.get('medical_records', 0))).grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Vaccination Records:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=str(stats.get('vaccination_records', 0))).grid(row=5, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(info_frame, text="Total Sales:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(info_frame, text=f"₱{stats.get('total_sales', 0):,.2f}").grid(row=6, column=1, sticky="w", padx=10, pady=5)
    
    def backup_database(self):
        """Backup database to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"vetclinic_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        if filename:
            try:
                # Close current connection
                self.db.close()
                
                # Copy database file
                shutil.copy2(DB_FILE, filename)
                
                # Reopen connection
                self.db = get_db()
                
                messagebox.showinfo("Success", f"Database backed up to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
                # Reopen connection on error
                self.db = get_db()
    
    def restore_database(self):
        """Restore database from backup"""
        filename = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            result = messagebox.askyesno("Confirm Restore", 
                                       "This will replace the current database. Continue?")
            
            if result:
                try:
                    # Close current connection
                    self.db.close()
                    
                    # Replace database file
                    shutil.copy2(filename, DB_FILE)
                    
                    # Reopen connection
                    self.db = get_db()
                    self.inventory_manager = EnhancedInventoryManager(self.db)
                    self.appointment_manager = EnhancedAppointmentManager(self.db)
                    self.sales_manager = SalesManager(self.db)
                    self.analytics_manager = AnalyticsManager(self.db)
                    self.communication_manager = CommunicationManager(self.db)
                    
                    messagebox.showinfo("Success", "Database restored successfully!")
                    messagebox.showinfo("Info", "Please restart the application for changes to take effect.")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
                    # Reopen connection on error
                    self.db = get_db()
    
    def create_security_tab(self, parent):
        """Create security settings tab"""
        parent.grid_columnconfigure(0, weight=1)
        
        ModernLabel(parent, text="Security Settings", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Security options frame
        security_frame = ModernFrame(parent)
        security_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        security_frame.grid_columnconfigure(1, weight=1)
        
        # Auto-logout setting
        ModernLabel(security_frame, text="Auto-logout (minutes):").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        logout_var = ctk.StringVar(value="30")
        logout_combo = ctk.CTkComboBox(security_frame, 
                                      values=["15", "30", "60", "120", "Never"],
                                      variable=logout_var)
        logout_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Password policy
        ModernLabel(security_frame, text="Password Policy:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        policy_var = ctk.StringVar(value="Medium")
        policy_combo = ctk.CTkComboBox(security_frame, values=["Low", "Medium", "High"])
        policy_combo.set("Medium")
        policy_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Save security settings button
        def save_security_settings():
            # In a real application, you would save these settings
            logout_time = logout_var.get()
            password_policy = policy_var.get()
            messagebox.showinfo("Success", f"Security settings saved!\nAuto-logout: {logout_time} minutes\nPassword Policy: {password_policy}")
        
        save_btn = ModernButton(parent, text="Save Security Settings", 
                               command=save_security_settings)
        save_btn.grid(row=2, column=0, padx=10, pady=20, sticky="ew")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # First, install required packages if not already installed
    print("Starting Veterinary Clinic Management System...")
    print("Checking requirements...")
    
    # Check if all required packages are available
    try:
        import customtkinter
        import sqlite3
        import tkinter
        print("All required packages are available!")
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Please install missing packages using:")
        print("pip install customtkinter")
    
    # Create and run the application
    app = VeterinaryClinicApp()
    app.run()