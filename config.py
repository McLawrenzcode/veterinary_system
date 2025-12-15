import os

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

# Application constants
APP_TITLE = "🐾 Veterinary Clinic Management System v2.0"
DB_FILE = "vetclinic.db"
THEME_MODE = "dark"

# Service prices for appointments
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

def get_db_path():
    """Get database file path"""
    return DB_FILE