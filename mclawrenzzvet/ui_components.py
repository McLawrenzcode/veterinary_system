import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from config import COLORS

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