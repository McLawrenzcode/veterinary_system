import customtkinter as ctk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry
from config import COLORS
from utils.helpers import generate_transaction_id
from utils.receipt_manager import ReceiptManager

class PointOfSaleModule:
    def __init__(self, app):
        self.app = app
        self.products_tree = None
        self.cart_tree = None
        self.customer_name_entry = None
        self.payment_method_combo = None
        self.total_label = None
    
    def show_pos(self):
        """Show point of sale screen"""
        self.app.clear_main_content()
        
        # Main POS frame
        pos_frame = ModernFrame(self.app.main_content)
        pos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        pos_frame.grid_rowconfigure(1, weight=1)
        pos_frame.grid_columnconfigure(0, weight=1)
        pos_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ModernLabel(pos_frame, text="💰 Point of Sale", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=20)
        
        # Create POS interface
        self.create_pos_interface(pos_frame)
    
    def create_pos_interface(self, parent):
        """Create complete point of sale interface"""
        # Left side - Products
        products_frame = ModernFrame(parent)
        products_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        products_frame.grid_rowconfigure(1, weight=1)
        products_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(products_frame, text="🛍️ Available Products", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", pady=10)
        
        # Products treeview
        products_columns = ("ID", "Name", "Price", "Stock", "Category")
        self.products_tree = ttk.Treeview(products_frame, columns=products_columns, show="headings", height=15)
        
        for col in products_columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Style products treeview
        style = ttk.Style()
        style.configure("Products.Treeview", 
                       background=COLORS["card"],
                       foreground=COLORS["text_light"],
                       fieldbackground=COLORS["card"])
        
        products_scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        self.products_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        products_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Add to cart button
        add_to_cart_btn = ModernButton(products_frame, text="➕ Add to Cart", 
                                      command=self.add_to_cart,
                                      fg_color=COLORS["success"])
        add_to_cart_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Right side - Cart and checkout
        cart_frame = ModernFrame(parent)
        cart_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        cart_frame.grid_rowconfigure(1, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(cart_frame, text="🛒 Shopping Cart", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).grid(row=0, column=0, sticky="w", pady=10)
        
        # Cart treeview
        cart_columns = ("Name", "Price", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=10)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        cart_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Cart controls
        cart_controls_frame = ModernFrame(cart_frame)
        cart_controls_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        cart_controls_frame.grid_columnconfigure((0, 1), weight=1)
        
        remove_item_btn = ModernButton(cart_controls_frame, text="➖ Remove Item", 
                                      command=self.remove_from_cart,
                                      fg_color=COLORS["warning"])
        remove_item_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        clear_cart_btn = ModernButton(cart_controls_frame, text="🗑️ Clear Cart", 
                                     command=self.clear_cart,
                                     fg_color=COLORS["danger"])
        clear_cart_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Customer info and totals
        info_frame = ModernFrame(cart_frame)
        info_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(info_frame, text="Customer Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.customer_name_entry = ModernEntry(info_frame)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ModernLabel(info_frame, text="Payment Method:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.payment_method_combo = ctk.CTkComboBox(info_frame, values=["Cash", "Credit Card", "GCash", "Bank Transfer"])
        self.payment_method_combo.set("Cash")
        self.payment_method_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Totals display
        totals_frame = ModernFrame(cart_frame)
        totals_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        totals_frame.grid_columnconfigure(1, weight=1)
        
        self.total_label = ModernLabel(totals_frame, text="Total: ₱0.00", 
                                      font=("Arial", 16, "bold"),
                                      text_color=COLORS["accent"])
        self.total_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Checkout button
        checkout_btn = ModernButton(cart_frame, text="💳 Checkout", 
                                   command=self.process_checkout,
                                   fg_color=COLORS["success"],
                                   font=("Arial", 14, "bold"))
        checkout_btn.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        # Load products
        self.load_products_for_pos()
        self.update_cart_display()
    
    def load_products_for_pos(self):
        """Load products for POS interface"""
        if not self.products_tree:
            return
            
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Get inventory items
        items = self.app.inventory_manager.get_all_items()
        
        # Populate products treeview
        for item in items:
            if item.stock > 0:  # Only show items with stock
                self.products_tree.insert("", "end", values=(
                    item.id,
                    item.name,
                    f"₱{item.price:.2f}",
                    item.stock,
                    item.category
                ))
    
    def add_to_cart(self):
        """Add selected product to cart"""
        if not self.products_tree:
            messagebox.showwarning("Warning", "No products loaded")
            return
            
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart")
            return
        
        item = self.products_tree.item(selection[0])
        values = item['values']
        
        item_id = values[0]
        item_name = values[1]
        item_price = float(values[2].replace('₱', ''))
        item_stock = values[3]
        
        # Check stock
        if item_stock <= 0:
            messagebox.showwarning("Warning", "This item is out of stock")
            return
        
        # Add to cart
        self.app.cart.add_item(item_id, item_name, item_price, 1, values[4])
        self.update_cart_display()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        if not self.cart_tree:
            messagebox.showwarning("Warning", "No cart loaded")
            return
            
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove from cart")
            return
        
        item = self.cart_tree.item(selection[0])
        values = item['values']
        
        # Find item ID by name (this is a simplification)
        for cart_item in self.app.cart.items:
            if cart_item.name == values[0]:
                self.app.cart.remove_item(cart_item.item_id)
                break
        
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.app.cart.clear()
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display with current items and total"""
        if not self.cart_tree or not self.total_label:
            return
            
        # Clear cart display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for item in self.app.cart.items:
            self.cart_tree.insert("", "end", values=(
                item.name,
                f"₱{item.price:.2f}",
                item.quantity,
                f"₱{item.subtotal:.2f}"
            ))
        
        # Update total
        self.total_label.configure(text=f"Total: ₱{self.app.cart.total:.2f}")
    
    def process_checkout(self):
        """Process the checkout and record sale"""
        if not self.app.cart.items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        # Validate customer name
        customer_name = self.customer_name_entry.get().strip()
        if not customer_name:
            customer_name = "Walk-in Customer"
        
        payment_method = self.payment_method_combo.get()
        
        # Check stock availability
        for cart_item in self.app.cart.items:
            # Get current stock from database
            items = self.app.inventory_manager.get_all_items()
            for item in items:
                if item.id == cart_item.item_id:
                    if item.stock < cart_item.quantity:
                        messagebox.showerror("Error", 
                                           f"Not enough stock for {item.name}. Available: {item.stock}")
                        return
                    break
        
        # Process sale
        transaction_id = generate_transaction_id()
        cart_items_dict = self.app.cart.to_legacy_format()
        
        if self.app.sales_manager.record_sale(transaction_id, cart_items_dict, 
                                            self.app.cart.total, payment_method, customer_name):
            # Generate receipt
            receipt_text = ReceiptManager.generate_receipt_text(
                transaction_id, 
                customer_name, 
                customer_name, 
                "Various", 
                "POS Sale", 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                self.app.cart.total, 
                cart_items_dict
            )
            
            # Show success message with receipt
            receipt_window = ctk.CTkToplevel(self.app.root)
            receipt_window.title("Sale Completed - Receipt")
            receipt_window.geometry("500x600")
            receipt_window.configure(fg_color=COLORS["background"])
            
            ModernLabel(receipt_window, text="✅ Sale Completed!", 
                       font=("Arial", 20, "bold"),
                       text_color=COLORS["success"]).pack(pady=20)
            
            receipt_frame = ModernFrame(receipt_window)
            receipt_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            receipt_text_widget = ctk.CTkTextbox(receipt_frame, font=("Courier", 12))
            receipt_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            receipt_text_widget.insert("1.0", receipt_text)
            receipt_text_widget.configure(state="disabled")
            
            # Save receipt button
            def save_receipt():
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile=f"receipt_{transaction_id}.txt"
                )
                if filename:
                    ReceiptManager.save_receipt_to_file(receipt_text, filename)
                    messagebox.showinfo("Success", f"Receipt saved as {filename}")
            
            save_btn = ModernButton(receipt_window, text="💾 Save Receipt", 
                                   command=save_receipt)
            save_btn.pack(pady=10)
            
            # Clear cart and refresh products
            self.app.cart.clear()
            self.update_cart_display()
            self.load_products_for_pos()
            if self.customer_name_entry:
                self.customer_name_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Sale completed! Transaction ID: {transaction_id}")
        else:
            messagebox.showerror("Error", "Failed to process sale")