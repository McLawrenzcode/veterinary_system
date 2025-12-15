import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, filedialog
import csv
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry, ColorfulCard
from config import COLORS

class ReportsModule:
    def __init__(self, app):
        self.app = app
        self.start_date_entry = None
        self.end_date_entry = None
        self.report_display_frame = None
    
    def show_reports(self):
        """Legacy reports - redirect to enhanced reports"""
        self.show_enhanced_reports()
    
    def show_enhanced_reports(self):
        """Show enhanced reports and analytics screen"""
        self.app.clear_main_content()
        
        # Main reports frame
        reports_frame = ModernFrame(self.app.main_content)
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
        if not self.report_display_frame:
            return
            
        # Clear display
        for widget in self.report_display_frame.winfo_children():
            widget.destroy()
        
        # Get enhanced report data
        total_sales = self.calculate_total_sales()
        total_appointments = len(self.app.appointment_manager.get_all_appointments())
        
        # Get inventory valuation
        inv_valuation = self.app.inventory_manager.get_inventory_valuation()
        total_inventory_value = inv_valuation[0] if inv_valuation else 0
        low_stock_items = inv_valuation[2] if inv_valuation else 0
        expiring_soon = inv_valuation[3] if inv_valuation else 0
        
        # Get popular services
        popular_services = self.app.analytics_manager.get_popular_services(limit=1)
        top_service = popular_services[0][0] if popular_services else "N/A"
        
        report_cards = [
            ("💰 Total Revenue", f"₱{total_sales:,.2f}", COLORS["success"]),
            ("📅 Total Appointments", f"{total_appointments}", COLORS["primary"]),
            ("📦 Inventory Value", f"₱{total_inventory_value:,.2f}", COLORS["secondary"]),
            ("⚠️ Low Stock Items", f"{low_stock_items}", COLORS["warning"]),
            ("⏰ Expiring Soon", f"{expiring_soon}", COLORS["danger"]),
            ("🏥 Top Service", top_service, COLORS["accent"])
        ]
        
        for i, (title, value, color) in enumerate(report_cards):
            row = i // 3
            col = i % 3
            card = ColorfulCard(self.report_display_frame, title, value, color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def generate_revenue_trends(self):
        """Generate and display revenue trends"""
        if not self.report_display_frame or not self.start_date_entry or not self.end_date_entry:
            return
            
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        revenue_data = self.app.analytics_manager.get_revenue_trends('monthly', start_date, end_date)
        
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
        if not self.report_display_frame or not self.start_date_entry or not self.end_date_entry:
            return
            
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        services = self.app.analytics_manager.get_popular_services(10, start_date, end_date)
        
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
        if not self.report_display_frame:
            return
            
        demographics = self.app.analytics_manager.get_customer_demographics()
        
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
        if not self.report_display_frame or not self.start_date_entry or not self.end_date_entry:
            return
            
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        performance = self.app.analytics_manager.get_veterinarian_performance(start_date, end_date)
        
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
                f"₱{vet[3]:.2f}",
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
    
    def calculate_total_sales(self):
        """Calculate total sales amount"""
        try:
            cur = self.app.db.cursor()
            cur.execute("SELECT SUM(total_amount) FROM sales")
            result = cur.fetchone()
            return result[0] or 0.0
        except Exception:
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
        export_dialog = ctk.CTkToplevel(self.app.root)
        export_dialog.title("Export Data")
        export_dialog.geometry("300x300")
        export_dialog.transient(self.app.root)
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
                    sales = self.app.sales_manager.get_sales_report()
                    writer.writerow(["Transaction ID", "Item ID", "Item Name", "Quantity", "Price", "Subtotal", "Total Amount", "Payment Method", "Customer Name", "Sale Date"])
                    for sale in sales:
                        writer.writerow(sale[1:11])  # Skip ID column
                
                elif data_type == "inventory":
                    # Export inventory data
                    items = self.app.inventory_manager.get_all_items()
                    writer.writerow(["ID", "Name", "Price", "Stock", "Category", "Image", "Brand", "Animal Type", "Dosage", "Expiration Date"])
                    for item in items:
                        writer.writerow([
                            item.id, item.name, item.price, item.stock, item.category,
                            "", item.brand, item.animal_type, item.dosage, item.expiration_date
                        ])
                
                elif data_type == "appointments":
                    # Export appointments data
                    appointments = self.app.appointment_manager.get_all_appointments()
                    writer.writerow(["Appointment ID", "Patient Name", "Owner Name", "Animal Type", "Date", "Notes", "Status", "Total Amount"])
                    for apt in appointments:
                        writer.writerow(apt[:8])  # Use first 8 columns
                
                elif data_type == "appointments_enhanced":
                    # Export enhanced appointments
                    appointments = self.app.appointment_manager.get_all_enhanced_appointments()
                    writer.writerow(["Appointment ID", "Patient Name", "Owner Name", "Animal Type", "Service", "Veterinarian", "Duration", "Appointment Date", "Appointment Time", "Date Created", "Notes", "Status", "Total Amount", "Reminder Sent", "Follow-up Needed"])
                    for apt in appointments:
                        writer.writerow(apt[1:16])  # Skip ID column
                
                elif data_type == "communication_log":
                    # Export communication log
                    log = self.app.communication_manager.get_communication_log()
                    writer.writerow(["Appointment ID", "Type", "To", "Message", "Date", "Status"])
                    for entry in log:
                        writer.writerow(entry[1:7])  # Skip ID column
        
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False