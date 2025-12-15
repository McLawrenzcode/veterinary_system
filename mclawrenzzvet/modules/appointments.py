import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
import tkinter as tk
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry, ResponsiveFrame, ColorfulCard
from config import COLORS, SERVICE_PRICES, VETERINARIANS
from utils.helpers import generate_appointment_id
from models import EnhancedAppointment

class AppointmentsModule:
    def __init__(self, app):
        self.app = app
        self.appointments_tree = None
    
    def show_appointments(self):
        """Show appointments management screen"""
        self.app.clear_main_content()
        
        # Main appointments frame
        appointments_frame = ModernFrame(self.app.main_content)
        appointments_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        appointments_frame.grid_rowconfigure(1, weight=1)
        appointments_frame.grid_columnconfigure(0, weight=1)
        
        # Title with icon
        title_label = ModernLabel(appointments_frame, text="📅 Appointment Management", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create appointment management interface
        self.create_appointments_interface(appointments_frame)
    
    def create_appointments_interface(self, parent):
        """Create appointments management interface"""
        # Button frame
        button_frame = ModernFrame(parent)
        button_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Action buttons with colors
        new_appt_btn = ModernButton(button_frame, text="➕ New Appointment", 
                                   command=self.create_enhanced_appointment,
                                   fg_color=COLORS["success"])
        new_appt_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        view_upcoming_btn = ModernButton(button_frame, text="📅 Upcoming", 
                                        command=self.show_upcoming_appointments,
                                        fg_color=COLORS["primary"])
        view_upcoming_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        view_appt_btn = ModernButton(button_frame, text="👁️ View Details", 
                                    command=self.view_appointments,
                                    fg_color=COLORS["secondary"])
        view_appt_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        update_appt_btn = ModernButton(button_frame, text="✏️ Update Status", 
                                      command=self.update_appointment_status,
                                      fg_color=COLORS["warning"])
        update_appt_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        delete_appt_btn = ModernButton(button_frame, text="🗑️ Delete", 
                                      command=self.delete_appointment,
                                      fg_color=COLORS["danger"])
        delete_appt_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # Appointments list frame
        list_frame = ModernFrame(parent)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview for appointments
        columns = ("ID", "Patient", "Owner", "Animal", "Date", "Time", "Vet", "Status", "Amount")
        self.appointments_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
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
            "ID": 120, "Patient": 120, "Owner": 120, "Animal": 100,
            "Date": 100, "Time": 80, "Vet": 120, "Status": 100, "Amount": 100
        }
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.appointments_tree.yview)
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.appointments_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load appointments data
        self.load_enhanced_appointments_data()
    
    def load_enhanced_appointments_data(self):
        """Load enhanced appointments data into the treeview"""
        if not self.appointments_tree:
            return
            
        # Clear existing data
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        # Get enhanced appointments
        appointments = self.app.appointment_manager.get_all_enhanced_appointments()
        
        if appointments:
            # Use enhanced appointments
            for apt in appointments:
                self.appointments_tree.insert("", "end", values=(
                    apt[1] if len(apt) > 1 else "",  # appointment_id
                    apt[2] if len(apt) > 2 else "",  # patient_name
                    apt[3] if len(apt) > 3 else "",  # owner_name
                    apt[4] if len(apt) > 4 else "",  # animal_type
                    apt[8] if len(apt) > 8 else "",  # appointment_date
                    apt[9] if len(apt) > 9 else "",  # appointment_time
                    apt[6] if len(apt) > 6 else "",  # veterinarian
                    apt[12] if len(apt) > 12 else "", # status
                    f"₱{apt[13]:.2f}" if len(apt) > 13 and apt[13] else "₱0.00"  # total_amount
                ))
        else:
            # Fallback to regular appointments
            appointments = self.app.appointment_manager.get_all_appointments()
            for apt in appointments:
                self.appointments_tree.insert("", "end", values=(
                    apt[0] if len(apt) > 0 else "",  # appointment_id
                    apt[1] if len(apt) > 1 else "",  # patient_name
                    apt[2] if len(apt) > 2 else "",  # owner_name
                    apt[3] if len(apt) > 3 else "",  # animal_type
                    apt[4] if len(apt) > 4 else "",  # date
                    "",  # time (not available)
                    "",  # vet (not available)
                    apt[6] if len(apt) > 6 else "", # status
                    f"₱{apt[7]:.2f}" if len(apt) > 7 and apt[7] else "₱0.00"  # total_amount
                ))
    
    def create_enhanced_appointment(self):
        """Create a new enhanced appointment dialog - FIXED VERSION"""
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("New Appointment - Enhanced")
        dialog.geometry("600x700")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["background"])
        
        # Responsive configuration
        if dialog.winfo_screenwidth() < 768:
            dialog.geometry("400x800")
        
        ModernLabel(dialog, text="Create New Appointment", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Form frame
        form_frame = ResponsiveFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        form_frame.configure_for_mobile()
        
        # Form fields with enhanced details
        fields = [
            ("Patient Name:", "entry"),
            ("Owner Name:", "entry"),
            ("Animal Type:", "combo", ["Dog", "Cat", "Bird", "Rabbit", "Other"]),
            ("Service Type:", "combo", list(SERVICE_PRICES.keys())),
            ("Veterinarian:", "combo", VETERINARIANS),
            ("Appointment Date:", "entry"),
            ("Appointment Time:", "combo", ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]),
            ("Duration (minutes):", "combo", ["30", "45", "60", "90", "120"]),
            ("Notes:", "text"),
            ("Status:", "combo", ["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"])
        ]
        
        entries = {}
        row = 0
        
        for field in fields:
            ModernLabel(form_frame, text=field[0]).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            if field[1] == "entry":
                if field[0] == "Appointment Date:":
                    # Set default to tomorrow
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    entry = ModernEntry(form_frame, width=300)
                    entry.insert(0, tomorrow)
                else:
                    entry = ModernEntry(form_frame, width=300)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ctk.CTkComboBox(form_frame, values=field[2], width=300)
                combo.set(field[2][0] if field[2] else "")
                combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = combo
                
                # Add price display for service type
                if field[0] == "Service Type:":
                    price_label = ModernLabel(form_frame, text="Price: ₱0.00", 
                                            text_color=COLORS["accent"])
                    price_label.grid(row=row, column=2, padx=10, pady=5)
                    
                    def update_price(event=None):
                        service = combo.get()
                        price = SERVICE_PRICES.get(service, 0.0)
                        price_label.configure(text=f"Price: ₱{price:.2f}")
                    
                    combo.configure(command=lambda e: update_price())
                    # Set initial price
                    update_price()
                    
            elif field[1] == "text":
                text_widget = ctk.CTkTextbox(form_frame, width=300, height=80)
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entries[field[0]] = text_widget
            
            row += 1
        
        # Submit button
        def submit_appointment():
            try:
                # Get form values
                patient_name = entries["Patient Name:"].get().strip()
                owner_name = entries["Owner Name:"].get().strip()
                animal_type = entries["Animal Type:"].get()
                service_type = entries["Service Type:"].get()
                veterinarian = entries["Veterinarian:"].get()
                appointment_date = entries["Appointment Date:"].get()
                appointment_time = entries["Appointment Time:"].get()
                duration = int(entries["Duration (minutes):"].get())
                notes = entries["Notes:"].get("1.0", "end-1c").strip() if hasattr(entries["Notes:"], 'get') else entries["Notes:"].get()
                status = entries["Status:"].get()
                
                # Validate required fields
                if not patient_name:
                    messagebox.showerror("Error", "Patient name is required")
                    return
                if not owner_name:
                    messagebox.showerror("Error", "Owner name is required")
                    return
                if not service_type:
                    messagebox.showerror("Error", "Service type is required")
                    return
                if not appointment_date:
                    messagebox.showerror("Error", "Appointment date is required")
                    return
                
                # Get service price
                price = SERVICE_PRICES.get(service_type, 0.0)
                # Check for veterinarian scheduling conflicts
                def _time_to_minutes(tstr):
                    try:
                        parts = tstr.split(":")
                        return int(parts[0]) * 60 + int(parts[1])
                    except Exception:
                        return None

                if veterinarian and appointment_date and appointment_time:
                    try:
                        existing = self.app.appointment_manager.get_appointments_by_veterinarian(veterinarian, appointment_date)
                        new_start = _time_to_minutes(appointment_time)
                        new_end = new_start + duration if new_start is not None else None

                        for ap in existing:
                            # ap format from appointments_enhanced: index 9=appointment_time, 7=duration, 12=status
                            existing_time = ap[9] if len(ap) > 9 else None
                            existing_duration = int(ap[7]) if len(ap) > 7 and ap[7] else None
                            existing_status = ap[12] if len(ap) > 12 else None

                            # Only consider scheduled or in-progress appointments
                            if existing_status and existing_status not in ("SCHEDULED", "IN_PROGRESS"):
                                continue

                            if existing_time and new_start is not None and existing_duration:
                                ex_start = _time_to_minutes(existing_time)
                                ex_end = ex_start + existing_duration
                                # Overlap check
                                if (new_start < ex_end) and (ex_start < new_end):
                                    messagebox.showerror("Scheduling Conflict",
                                                         f"Dr. {veterinarian} already has an appointment at {existing_time}. Please choose a different time or doctor.")
                                    return
                    except Exception as e:
                        print(f"Error checking vet schedule: {e}")

                # Create enhanced appointment object
                appointment = EnhancedAppointment(
                    appointment_id=generate_appointment_id(),
                    patient_name=patient_name,
                    owner_name=owner_name,
                    animal_type=animal_type,
                    service=service_type,
                    notes=notes,
                    status=status,
                    veterinarian=veterinarian,
                    duration=duration,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
                
                # Add service with proper pricing
                appointment.add_service(service_type, 1, price, price)
                
                # Debug: Print appointment details
                print(f"Creating appointment: {appointment.appointment_id}")
                print(f"Patient: {appointment.patient_name}")
                print(f"Owner: {appointment.owner_name}")
                print(f"Service: {appointment.service}")
                print(f"Services list: {appointment.services}")
                print(f"Total amount: {appointment.total_amount}")
                print(f"Date: {appointment.date_created}")
                print(f"Status: {appointment.status}")
                
                # Save to database - try enhanced first, then legacy
                try:
                    # First try enhanced appointment
                    if self.app.appointment_manager.record_enhanced_appointment(appointment):
                        print("Enhanced appointment recorded successfully")
                    else:
                        print("Failed to record enhanced appointment")
                    
                    # Always try to record to legacy appointments table
                    if self.app.appointment_manager.record_appointment(appointment):
                        print("Legacy appointment recorded successfully")
                        messagebox.showinfo("Success", "Appointment created successfully!")
                        dialog.destroy()
                        self.load_enhanced_appointments_data()
                    else:
                        messagebox.showerror("Error", "Failed to create appointment in main database")
                        
                except Exception as db_error:
                    print(f"Database error: {db_error}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Database Error", f"Failed to create appointment: {str(db_error)}")
                    
            except Exception as e:
                print(f"Appointment creation error: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to create appointment: {str(e)}")
        
        submit_btn = ModernButton(dialog, text="Create Appointment", 
                                 command=submit_appointment,
                                 fg_color=COLORS["success"], 
                                 hover_color="#218838")
        submit_btn.pack(pady=20)
    
    def show_upcoming_appointments(self):
        """Show upcoming appointments"""
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("Upcoming Appointments")
        dialog.geometry("800x500")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="📅 Upcoming Appointments (Next 7 Days)", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        # Create treeview for upcoming appointments
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Patient", "Owner", "Animal", "Date", "Time", "Vet", "Service", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load upcoming appointments
        upcoming = self.app.appointment_manager.get_upcoming_appointments(7)
        
        for apt in upcoming:
            if len(apt) >= 9:  # Enhanced appointment
                tree.insert("", "end", values=(
                    apt[1], apt[2], apt[3], apt[4], apt[8], apt[9], apt[6], apt[5], apt[12]
                ))
        
        # Add reminder button
        def send_reminder():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an appointment")
                return
            
            item = tree.item(selection[0])
            values = item['values']
            appointment_id = values[0]
            
            if self.app.appointment_manager.send_appointment_reminder(appointment_id):
                messagebox.showinfo("Success", "Reminder sent successfully!")
            else:
                messagebox.showinfo("Info", "Reminder already sent or not needed")
        
        if self.app.current_user.has_permission('manage_communications'):
            reminder_btn = ModernButton(dialog, text="🔔 Send Reminder", 
                                      command=send_reminder,
                                      fg_color=COLORS["warning"])
            reminder_btn.pack(pady=10)
    
    def view_appointments(self):
        """View selected appointment details"""
        if not self.appointments_tree:
            messagebox.showwarning("Warning", "No appointments loaded")
            return
            
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to view")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        
        # Show appointment details
        details_window = ctk.CTkToplevel(self.app.root)
        details_window.title("Appointment Details")
        details_window.geometry("500x400")
        details_window.configure(fg_color=COLORS["background"])
        
        ModernLabel(details_window, text="📋 Appointment Details", 
                   font=("Arial", 18, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        details_frame = ModernFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        details_text = f"Appointment ID: {values[0]}\n"
        details_text += f"Patient: {values[1]}\n"
        details_text += f"Owner: {values[2]}\n"
        details_text += f"Animal Type: {values[3]}\n"
        details_text += f"Date: {values[4]}\n"
        if values[5]:  # Time
            details_text += f"Time: {values[5]}\n"
        if values[6]:  # Veterinarian
            details_text += f"Veterinarian: {values[6]}\n"
        details_text += f"Status: {values[7]}\n"
        details_text += f"Amount: {values[8]}"
        
        details_label = ModernLabel(details_frame, text=details_text,
                                   font=("Arial", 12),
                                   justify="left")
        details_label.pack(padx=20, pady=20)
        
        # Add follow-up button if user has permission
        if self.app.current_user.has_permission('manage_communications'):
            def send_follow_up():
                message = f"Follow-up for appointment {values[0]}"
                if self.app.communication_manager.send_follow_up(values[0], message):
                    messagebox.showinfo("Success", "Follow-up sent successfully!")
                else:
                    messagebox.showinfo("Info", "Follow-up not sent")
            
            follow_up_btn = ModernButton(details_window, text="✉️ Send Follow-up", 
                                       command=send_follow_up,
                                       fg_color=COLORS["success"])
            follow_up_btn.pack(pady=10)
    
    def update_appointment_status(self):
        """Update appointment status"""
        if not self.appointments_tree:
            messagebox.showwarning("Warning", "No appointments loaded")
            return
            
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to update")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        appointment_id = values[0]
        
        # Status selection dialog
        status_dialog = ctk.CTkToplevel(self.app.root)
        status_dialog.title("Update Status")
        status_dialog.geometry("300x200")
        status_dialog.transient(self.app.root)
        status_dialog.grab_set()
        status_dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(status_dialog, text="Select New Status", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        status_var = ctk.StringVar(value=values[7] if len(values) > 7 else "SCHEDULED")
        status_combo = ctk.CTkComboBox(status_dialog, 
                                      values=["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"],
                                      variable=status_var)
        status_combo.pack(pady=10)
        
        def update_status():
            new_status = status_var.get()
            if self.app.appointment_manager.update_appointment_status(appointment_id, new_status):
                messagebox.showinfo("Success", "Status updated successfully!")
                self.load_enhanced_appointments_data()
                status_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update status")
        
        update_btn = ModernButton(status_dialog, text="Update Status", 
                                command=update_status,
                                fg_color=COLORS["success"])
        update_btn.pack(pady=20)
    
    def delete_appointment(self):
        """Delete selected appointment"""
        if not self.appointments_tree:
            messagebox.showwarning("Warning", "No appointments loaded")
            return
            
        selection = self.appointments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an appointment to delete")
            return
        
        item = self.appointments_tree.item(selection[0])
        values = item['values']
        appointment_id = values[0]
        
        # Confirmation dialog
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete appointment {appointment_id}?")
        
        if result:
            if self.app.appointment_manager.delete_appointment(appointment_id):
                messagebox.showinfo("Success", "Appointment deleted successfully!")
                self.load_enhanced_appointments_data()
            else:
                messagebox.showerror("Error", "Failed to delete appointment")