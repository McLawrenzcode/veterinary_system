import sqlite3
from datetime import datetime, timedelta
from models import Medicine, CartItem, ShoppingCart
from database import get_db

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