import customtkinter as ctk
from datetime import datetime
from tkinter import ttk, messagebox
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry, ColorfulCard
from config import COLORS
from models import Medicine

class InventoryModule:
    def __init__(self, app):
        self.app = app
        self.inventory_tree = None
        self.search_entry = None
    
    def show_inventory(self):
        """Show inventory management screen with enhanced features"""
        self.app.clear_main_content()
        
        # Main inventory frame
        inventory_frame = ModernFrame(self.app.main_content)
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
        if not self.inventory_tree:
            return
            
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get inventory items
        items = self.app.inventory_manager.get_all_items()
        
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
        dialog = ctk.CTkToplevel(self.app.root)
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
        low_stock_items = self.app.inventory_manager.get_low_stock_items(10)
        
        for item in low_stock_items:
            tree.insert("", "end", values=(
                item[0], item[1], item[4], item[3], f"₱{item[2]:.2f}", item[7]
            ))
    
    def show_expiring_items(self):
        """Show expiring items"""
        dialog = ctk.CTkToplevel(self.app.root)
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
        expiring_items = self.app.inventory_manager.get_expiring_items(30)
        
        for item in expiring_items:
            days_left = int(item[10]) if len(item) > 10 else 0
            tree.insert("", "end", values=(
                item[0], item[1], item[9], days_left, item[3], item[4], f"₱{item[2]:.2f}"
            ))
    
    def search_inventory(self):
        """Search inventory items"""
        if not self.search_entry or not self.inventory_tree:
            return
            
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_inventory_data()
            return
        
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Search items
        items = self.app.inventory_manager.search_items(search_term)
        
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
    
    def add_inventory_item(self):
        """Add new inventory item"""
        self.show_inventory_item_dialog()
    
    def edit_inventory_item(self):
        """Edit selected inventory item"""
        if not self.inventory_tree:
            messagebox.showwarning("Warning", "No inventory loaded")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = self.inventory_tree.item(selection[0])
        values = item['values']
        item_id = values[0]
        
        # Get the full item details
        items = self.app.inventory_manager.get_all_items()
        selected_item = None
        for item_obj in items:
            if item_obj.id == item_id:
                selected_item = item_obj
                break
        
        if selected_item:
            self.show_inventory_item_dialog(selected_item)
    
    def delete_inventory_item(self):
        """Delete selected inventory item"""
        if not self.inventory_tree:
            messagebox.showwarning("Warning", "No inventory loaded")
            return
            
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
            if self.app.inventory_manager.delete_item(item_id):
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.load_inventory_data()
            else:
                messagebox.showerror("Error", "Failed to delete item")
    
    def show_inventory_item_dialog(self, item=None):
        """Show dialog for adding/editing inventory items"""
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("Add Item" if item is None else "Edit Item")
        dialog.geometry("500x650")
        dialog.transient(self.app.root)
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
                    success = self.app.inventory_manager.add_item(medicine)
                else:
                    success = self.app.inventory_manager.update_item(medicine)
                
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