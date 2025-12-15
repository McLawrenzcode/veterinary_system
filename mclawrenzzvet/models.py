import sqlite3
from datetime import datetime, timedelta

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