from datetime import datetime
import tkinter as tk

def generate_appointment_id():
    """Generate unique appointment ID"""
    return f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"


def generate_transaction_id():
    """Generate unique transaction ID"""
    return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"


def validate_number(value: str) -> bool:
    """Validate if string is a valid number"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def apply_theme(window=None):
    """Apply theme to the application"""
    import customtkinter as ctk
    from config import THEME_MODE
    
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme("blue")
    if window is not None:
        try:
            window.update()
        except tk.TclError:
            pass