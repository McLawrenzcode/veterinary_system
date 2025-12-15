import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3

from ui_components import ModernFrame, ModernLabel, ModernEntry, ModernButton
from config import COLORS
from models import EnhancedUser

class AuthenticationModule:
    def __init__(self, app):
        self.app = app
    
    def show_login_screen(self):
        """Show the login screen with Show Password toggle"""
        self.app.clear_main_content()
        
        login_frame = ModernFrame(self.app.main_content)
        login_frame.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
        login_frame.grid_rowconfigure(5, weight=1)
        login_frame.grid_columnconfigure(0, weight=1)
        
        # Title with color
        title_label = ModernLabel(login_frame, text="Veterinary Clinic Login", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, pady=40)
        
        # Username
        ModernLabel(login_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ModernEntry(login_frame, placeholder_text="Enter username")
        self.username_entry.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Password frame (to hold password entry and show/hide button)
        password_frame = ModernFrame(login_frame, fg_color="transparent")
        password_frame.grid(row=2, column=0, pady=5, sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(password_frame, text="Password:").grid(row=0, column=0, sticky="w")
        
        # Password entry with show/hide toggle
        password_frame_inner = ModernFrame(password_frame, fg_color="transparent")
        password_frame_inner.grid(row=1, column=0, sticky="ew")
        password_frame_inner.grid_columnconfigure(0, weight=1)
        
        self.password_entry = ModernEntry(password_frame_inner, placeholder_text="Enter password", show="•")
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Show/Hide Password button
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_btn = ModernButton(
            password_frame_inner, 
            text="👁️", 
            width=40,
            command=self.toggle_password_visibility,
            fg_color="transparent",
            hover_color=COLORS["dark"]
        )
        self.show_password_btn.grid(row=0, column=1, sticky="e")
        
        # Login button
        login_btn = ModernButton(login_frame, text="Login", 
                                command=self.perform_login,
                                fg_color=COLORS["success"])
        login_btn.grid(row=3, column=0, pady=20, sticky="ew")
        
        # Default credentials hint
        hint_label = ModernLabel(login_frame, 
                                text="Default: admin/admin123, staff/staff123, vet_smith/vet123, reception/recep123",
                                text_color=COLORS["accent"],
                                font=("Arial", 10))
        hint_label.grid(row=4, column=0, pady=10)
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.perform_login())
        self.password_entry.bind("<Return>", lambda e: self.perform_login())
        
        # Set focus to username field
        self.username_entry.focus()
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            # Hide password
            self.password_entry.configure(show="•")
            self.show_password_btn.configure(text="👁️")
            self.show_password_var.set(False)
        else:
            # Show password
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text="👁️‍🗨️")
            self.show_password_var.set(True)
    
    def perform_login(self):
        """Perform login with current credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.login(username, password)
    
    def login(self, username, password):
        """Handle user login - FIXED VERSION"""
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            conn = self.app.db
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                       (username, password))
            user_data = cur.fetchone()
            
            if user_data:
                # Handle users with and without role field
                # The database might have old users without role column
                if len(user_data) >= 4:  # Has role column
                    user_id, username, password, role = user_data[0], user_data[1], user_data[2], user_data[3]
                else:  # Old user without role column
                    user_id, username, password = user_data[0], user_data[1], user_data[2]
                    role = "staff"  # Default role
                
                self.app.current_user = EnhancedUser(user_id, username, password, role)
                self.app.setup_navigation()
                self.app.show_dashboard()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")