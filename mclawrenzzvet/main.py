import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta

# Import modules
from config import APP_TITLE, COLORS, THEME_MODE
from database import get_db, init_db
from managers import EnhancedInventoryManager, EnhancedAppointmentManager, SalesManager, AnalyticsManager, CommunicationManager
from models import EnhancedUser, ShoppingCart
from ui_components import ModernFrame
from utils.helpers import apply_theme
from modules import (
    AuthenticationModule,
    AppointmentsModule,
    InventoryModule,
    PointOfSaleModule,
    ReportsModule,
    CommunicationsModule,
    SettingsModule
)

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
        init_db()
        
        # Import here to avoid circular import; optional population
        try:
            from data_catalogs import populate_initial_inventory
            print("Populating initial inventory...")
            populate_initial_inventory()
        except ImportError:
            print("No data_catalogs module found — skipping initial inventory population")
        
        # Initialize managers
        self.db = get_db()
        self.inventory_manager = EnhancedInventoryManager(self.db)
        self.appointment_manager = EnhancedAppointmentManager(self.db)
        self.sales_manager = SalesManager(self.db)
        self.analytics_manager = AnalyticsManager(self.db)
        self.communication_manager = CommunicationManager(self.db)
        self.cart = ShoppingCart()
        self.current_user = None
        
        # Initialize modules
        self.modules = {
            'auth': AuthenticationModule(self),
            'appointments': AppointmentsModule(self),
            'inventory': InventoryModule(self),
            'pos': PointOfSaleModule(self),
            'reports': ReportsModule(self),
            'communications': CommunicationsModule(self),
            'settings': SettingsModule(self)
        }
        
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
        self.modules['auth'].show_login_screen()
        
    def create_sidebar(self):
        """Create the sidebar navigation"""
        self.sidebar = ModernFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(9, weight=1)
        
        # Title with color
        from ui_components import ModernLabel
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
            ("📅 Appointments", self.modules['appointments'].show_appointments),
            ("📦 Inventory", self.modules['inventory'].show_inventory),
            ("💰 Point of Sale", self.modules['pos'].show_pos),
            ("📊 Reports", self.modules['reports'].show_reports),
        ]
        
        # Add role-based features
        if self.current_user.has_permission('manage_communications'):
            nav_items.append(("✉️ Communications", self.modules['communications'].show_communications))
        
        nav_items.append(("⚙️ Settings", self.modules['settings'].show_settings))
        
        for i, (text, command) in enumerate(nav_items, 1):
            from ui_components import ModernButton
            btn = ModernButton(self.sidebar, text=text, command=command,
                              fg_color="transparent", 
                              border_color=COLORS["primary"],
                              hover_color=COLORS["secondary"],
                              text_color=COLORS["text_light"])
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
        
        # Add user role indicator
        from ui_components import ModernLabel
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
    
    def show_dashboard(self):
        """Show the dashboard screen"""
        self.clear_main_content()
        
        # Main dashboard frame
        from ui_components import ModernFrame, ModernLabel, ColorfulCard
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
        
        # Get actual statistics
        total_items = len(self.inventory_manager.get_all_items())
        appointments = self.appointment_manager.get_all_appointments()
        unique_appointments = set()
        today_unique_appointments = set()
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        for apt in appointments:
            if len(apt) > 0 and apt[0]:
                unique_appointments.add(apt[0])
                if len(apt) > 4 and apt[4] and apt[4].startswith(today_str):
                    today_unique_appointments.add(apt[0])
        
        total_appointments_count = len(unique_appointments)
        today_appointments_count = len(today_unique_appointments)
        
        # Get expiring items
        expiring_items = len(self.inventory_manager.get_expiring_items(30))
        low_stock = len(self.inventory_manager.get_low_stock_items(10))
        
        # Get upcoming appointments
        upcoming_appointments = len(self.appointment_manager.get_upcoming_appointments(7))
        
        stats_data = [
            ("Total Inventory", f"{total_items} items", COLORS["primary"]),
            ("Today's Appointments", f"{today_appointments_count}", COLORS["success"]),
            ("Upcoming (7 days)", f"{upcoming_appointments}", COLORS["secondary"]),
            ("Low Stock Items", f"{low_stock}", COLORS["warning"]),
            ("Expiring Soon", f"{expiring_items}", COLORS["danger"]),
            ("All Appointments", f"{total_appointments_count}", COLORS["accent"])
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
        from ui_components import ModernButton
        quick_actions = [
            ("➕ New Appointment", self.modules['appointments'].create_enhanced_appointment, COLORS["success"]),
            ("📦 Manage Inventory", self.modules['inventory'].show_inventory, COLORS["primary"]),
            ("💰 POS Sale", self.modules['pos'].show_pos, COLORS["secondary"]),
            ("📊 View Reports", self.modules['reports'].show_enhanced_reports, COLORS["warning"])
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            btn = ModernButton(actions_frame, text=text, command=command,
                             fg_color=color, hover_color=COLORS["dark"])
            btn.grid(row=1, column=i, padx=10, pady=10, sticky="nsew")
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        # Clear navigation buttons
        for btn in self.nav_buttons.values():
            btn.destroy()
        self.nav_buttons.clear()
        self.modules['auth'].show_login_screen()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point for the application"""
    try:
        # Create and run the application
        app = VeterinaryClinicApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()