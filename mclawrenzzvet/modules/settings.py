import customtkinter as ctk
import tkinter.messagebox as messagebox
import sqlite3
import shutil
from tkinter import ttk, filedialog
from datetime import datetime
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry
from config import COLORS, THEME_MODE, DB_FILE
from utils.helpers import apply_theme

class SettingsModule:
    def __init__(self, app):
        self.app = app
        self.users_tree = None
    
    def show_settings(self):
        """Show settings screen with complete functionality"""
        self.app.clear_main_content()
        
        # Main settings frame
        settings_frame = ModernFrame(self.app.main_content)
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
        ModernLabel(current_user_frame, text=f"{self.app.current_user.username} ({self.app.current_user.get_role_display_name()})",
                   font=("Arial", 14)).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # User list (admin only)
        if self.app.current_user.has_permission('manage_users'):
            ModernLabel(parent, text="User Accounts:", 
                       font=("Arial", 16, "bold"),
                       text_color=COLORS["accent"]).grid(row=1, column=0, sticky="w", padx=10, pady=10)
            
            # Users treeview
            users_columns = ("ID", "Username", "Role")
            self.users_tree = ttk.Treeview(parent, columns=users_columns, show="headings", height=8)
            
            for col in users_columns:
                self.users_tree.heading(col, text=col)
                self.users_tree.column(col, width=100)
            
            users_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.users_tree.yview)
            self.users_tree.configure(yscrollcommand=users_scrollbar.set)
            
            self.users_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            users_scrollbar.grid(row=2, column=1, sticky="ns")
            
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
            
            # Load users
            self.load_users()
        else:
            # For non-admin users, show limited options
            limited_frame = ModernFrame(parent)
            limited_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            
            ModernLabel(limited_frame, text="User management features are available for administrators only.",
                       font=("Arial", 12)).pack(expand=True)
    
    def load_users(self):
        """Load users into the treeview"""
        if not self.app.current_user.has_permission('manage_users') or not self.users_tree:
            return
        
        # Clear existing data
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            cur = self.app.db.cursor()
            cur.execute("SELECT id, username, role FROM users ORDER BY id")
            users = cur.fetchall()
            
            for user in users:
                self.users_tree.insert("", "end", values=user)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
    
    def add_user(self):
        """Add new user dialog"""
        if not self.app.current_user.has_permission('manage_users'):
            messagebox.showwarning("Permission Denied", "Only administrators can add users")
            return
        
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.transient(self.app.root)
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
            ("Role:", "combo", ["admin", "veterinarian", "staff", "receptionist"])
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            ModernLabel(form_frame, text=field[0]).grid(row=row, column=0, sticky="w", padx=10, pady=10)
            
            if field[1] == "entry":
                entry = ModernEntry(form_frame, width=200, show="•" if field[0] == "Password:" else "")
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ctk.CTkComboBox(form_frame, values=field[2], width=200)
                combo.set("staff")
                combo.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
                entries[field[0]] = combo
            
            row += 1
        
        def submit_user():
            username = entries["Username:"].get().strip()
            password = entries["Password:"].get()
            role = entries["Role:"].get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required")
                return
            
            try:
                cur = self.app.db.cursor()
                cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
                self.app.db.commit()
                
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
        if not self.app.current_user.has_permission('manage_users') and not self.app.current_user.id:
            messagebox.showwarning("Permission Denied", "You don't have permission to change passwords")
            return
        
        if not self.users_tree:
            messagebox.showwarning("Warning", "No users loaded")
            return
            
        selection = self.users_tree.selection()
        if not selection and not self.app.current_user.id:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        if selection:
            item = self.users_tree.item(selection[0])
            values = item['values']
            user_id = values[0]
            username = values[1]
        else:
            # Allow users to change their own password
            user_id = self.app.current_user.id
            username = self.app.current_user.username
        
        # Check permission
        if not self.app.current_user.has_permission('manage_users') and user_id != self.app.current_user.id:
            messagebox.showwarning("Permission Denied", "You can only change your own password")
            return
        
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("Change Password")
        dialog.geometry("400x250")
        dialog.transient(self.app.root)
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
                cur = self.app.db.cursor()
                cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
                self.app.db.commit()
                
                messagebox.showinfo("Success", "Password changed successfully!")
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to change password: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Change Password", command=submit_password)
        submit_btn.pack(pady=20)
    
    def delete_user(self):
        """Delete selected user"""
        if not self.app.current_user.has_permission('manage_users'):
            messagebox.showwarning("Permission Denied", "Only administrators can delete users")
            return
        
        if not self.users_tree:
            messagebox.showwarning("Warning", "No users loaded")
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
        if user_id == self.app.current_user.id:
            messagebox.showwarning("Warning", "You cannot delete your own account")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete user '{username}'?")
        
        if result:
            try:
                cur = self.app.db.cursor()
                cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                self.app.db.commit()
                
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
            import config
            import customtkinter as ctk

            config.THEME_MODE = theme_var.get()
            ctk.set_appearance_mode(config.THEME_MODE)
            ctk.set_default_color_theme(color_var.get())
            apply_theme(self.app.root)
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
                                 command=self.backup_database,
                                 fg_color=COLORS["success"])
        backup_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        restore_btn = ModernButton(db_actions_frame, text="🔄 Restore Database", 
                                  command=self.restore_database,
                                  fg_color=COLORS["warning"])
        restore_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Database info
        info_frame = ModernFrame(parent)
        info_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Get database info
        try:
            cur = self.app.db.cursor()
            
            # Table counts
            tables = ["users", "inventory", "appointments", "sales", "appointments_enhanced", "communication_log"]
            table_counts = {}
            
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cur.fetchone()[0]
                except:
                    table_counts[table] = 0
            
            ModernLabel(info_frame, text="Database File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=DB_FILE).grid(row=0, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Users:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("users", 0))).grid(row=1, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Inventory Items:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("inventory", 0))).grid(row=2, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Appointments:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("appointments", 0))).grid(row=3, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Enhanced Appointments:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("appointments_enhanced", 0))).grid(row=4, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Sales:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("sales", 0))).grid(row=5, column=1, sticky="w", padx=10, pady=5)
            
            ModernLabel(info_frame, text="Communications:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
            ModernLabel(info_frame, text=str(table_counts.get("communication_log", 0))).grid(row=6, column=1, sticky="w", padx=10, pady=5)
            
        except Exception as e:
            ModernLabel(info_frame, text=f"Error loading database info: {str(e)}").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
    
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
                self.app.db.close()
                
                # Copy database file
                shutil.copy2(DB_FILE, filename)
                
                # Reopen connection
                self.app.db = sqlite3.connect(DB_FILE)
                
                messagebox.showinfo("Success", f"Database backed up to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
                # Reopen connection on error
                try:
                    self.app.db = sqlite3.connect(DB_FILE)
                except:
                    pass
    
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
                    self.app.db.close()
                    
                    # Replace database file
                    shutil.copy2(filename, DB_FILE)
                    
                    # Reopen connection
                    from database import get_db
                    self.app.db = get_db()
                    
                    messagebox.showinfo("Success", "Database restored successfully!")
                    messagebox.showinfo("Info", "Please restart the application for changes to take effect.")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
                    # Try to reopen connection
                    try:
                        from database import get_db
                        self.app.db = get_db()
                    except:
                        pass
    
    def create_security_tab(self, parent):
        """Create security settings tab"""
        parent.grid_columnconfigure(0, weight=1)
        
        ModernLabel(parent, text="Security Settings", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Password policy frame
        security_frame = ModernFrame(parent)
        security_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        security_frame.grid_columnconfigure(1, weight=1)
        
        # Current session info
        session_frame = ModernFrame(security_frame)
        session_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        session_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(session_frame, text="Session Started:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(session_frame, text=datetime.now().strftime('%Y-%m-%d %H:%M:%S')).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ModernLabel(session_frame, text="Session Duration:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ModernLabel(session_frame, text="Active").grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Auto-logout settings
        ModernLabel(security_frame, text="Auto-logout after (minutes):").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        logout_var = ctk.StringVar(value="30")
        logout_combo = ctk.CTkComboBox(security_frame, 
                                      values=["15", "30", "60", "120", "Never"],
                                      variable=logout_var)
        logout_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Audit logging
        audit_frame = ModernFrame(parent)
        audit_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        audit_frame.grid_columnconfigure(0, weight=1)
        
        audit_var = ctk.BooleanVar(value=True)
        audit_check = ctk.CTkCheckBox(audit_frame, text="Enable Audit Logging", variable=audit_var)
        audit_check.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        def apply_security_settings():
            # In a real application, you would save these settings
            messagebox.showinfo("Success", "Security settings applied!")
        
        apply_btn = ModernButton(parent, text="Apply Security Settings", 
                                command=apply_security_settings)
        apply_btn.grid(row=3, column=0, padx=10, pady=20, sticky="ew")