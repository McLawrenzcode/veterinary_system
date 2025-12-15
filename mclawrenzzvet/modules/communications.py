import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
from ui_components import ModernFrame, ModernLabel, ModernButton, ModernEntry
from config import COLORS

class CommunicationsModule:
    def __init__(self, app):
        self.app = app
    
    def show_communications(self):
        """Show communications management interface"""
        if not self.app.current_user.has_permission('manage_communications'):
            messagebox.showwarning("Access Denied", 
                                 "You don't have permission to access communications")
            return
        
        self.app.clear_main_content()
        
        # Main communications frame
        comm_frame = ModernFrame(self.app.main_content)
        comm_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        comm_frame.grid_rowconfigure(1, weight=1)
        comm_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ModernLabel(comm_frame, text="✉️ Communications", 
                                 font=("Arial", 24, "bold"),
                                 text_color=COLORS["accent"])
        title_label.grid(row=0, column=0, sticky="w", pady=20)
        
        # Create communications interface
        self.create_communications_interface(comm_frame)
    
    def create_communications_interface(self, parent):
        """Create communications management interface"""
        # Controls frame
        controls_frame = ModernFrame(parent)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(controls_frame, text="Search:").grid(row=0, column=0, padx=10, pady=10)
        search_entry = ModernEntry(controls_frame, placeholder_text="Search communications...")
        search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        def search_communications():
            search_term = search_entry.get().strip()
            # Implement search functionality here
            messagebox.showinfo("Search", f"Searching for: {search_term}")
        
        search_btn = ModernButton(controls_frame, text="🔍 Search", 
                                 command=search_communications)
        search_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Action buttons
        action_frame = ModernFrame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        view_log_btn = ModernButton(action_frame, text="📋 View Log", 
                                   command=self.view_communication_log,
                                   fg_color=COLORS["primary"])
        view_log_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        send_reminders_btn = ModernButton(action_frame, text="🔔 Send Reminders", 
                                         command=self.send_bulk_reminders,
                                         fg_color=COLORS["warning"])
        send_reminders_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        follow_up_btn = ModernButton(action_frame, text="✉️ Follow-up", 
                                    command=self.send_bulk_followups,
                                    fg_color=COLORS["success"])
        follow_up_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Communications display frame
        display_frame = ModernFrame(parent)
        display_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(display_frame, text="Communication Dashboard", 
                   font=("Arial", 16, "bold"),
                   text_color=COLORS["accent"]).pack(pady=10)
        
        # Display communication statistics
        stats = self.get_communication_stats()
        
        stats_text = f"""
        📊 Communication Statistics:
        
        • Total Communications Sent: {stats.get('total', 0)}
        • Reminders Sent: {stats.get('reminders', 0)}
        • Follow-ups Sent: {stats.get('followups', 0)}
        • Pending Follow-ups: {stats.get('pending_followups', 0)}
        
        Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        stats_label = ModernLabel(display_frame, text=stats_text,
                                 font=("Arial", 12),
                                 justify="left")
        stats_label.pack(padx=20, pady=20)
    
    def get_communication_stats(self):
        """Get communication statistics"""
        try:
            cur = self.app.db.cursor()
            
            # Check if communication log table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_log'")
            if not cur.fetchone():
                return {'total': 0, 'reminders': 0, 'followups': 0, 'pending_followups': 0}
            
            # Get total communications
            cur.execute("SELECT COUNT(*) FROM communication_log")
            total = cur.fetchone()[0]
            
            # Get reminders count
            cur.execute("SELECT COUNT(*) FROM communication_log WHERE communication_type = 'REMINDER'")
            reminders = cur.fetchone()[0]
            
            # Get follow-ups count
            cur.execute("SELECT COUNT(*) FROM communication_log WHERE communication_type = 'FOLLOW_UP'")
            followups = cur.fetchone()[0]
            
            # Get pending follow-ups from appointments
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if cur.fetchone():
                cur.execute("SELECT COUNT(*) FROM appointments_enhanced WHERE follow_up_needed = 1")
                pending_followups = cur.fetchone()[0]
            else:
                pending_followups = 0
            
            return {
                'total': total,
                'reminders': reminders,
                'followups': followups,
                'pending_followups': pending_followups
            }
            
        except Exception as e:
            print(f"Error getting communication stats: {e}")
            return {'total': 0, 'reminders': 0, 'followups': 0, 'pending_followups': 0}
    
    def view_communication_log(self):
        """View communication log"""
        log = self.app.communication_manager.get_communication_log()
        
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title("Communication Log")
        dialog.geometry("800x500")
        dialog.configure(fg_color=COLORS["background"])
        
        ModernLabel(dialog, text="📋 Communication Log", 
                   font=("Arial", 20, "bold"),
                   text_color=COLORS["accent"]).pack(pady=20)
        
        if not log:
            ModernLabel(dialog, text="No communication records found.").pack(expand=True)
            return
        
        # Create treeview
        frame = ModernFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        columns = ("Date", "Type", "To", "Message", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate log
        for entry in log:
            tree.insert("", "end", values=(
                entry[5] if len(entry) > 5 else "",  # sent_date
                entry[2] if len(entry) > 2 else "",  # communication_type
                entry[3] if len(entry) > 3 else "",  # sent_to
                (entry[4][:50] + "...") if len(entry) > 4 and len(entry[4]) > 50 else (entry[4] if len(entry) > 4 else ""),  # message
                entry[6] if len(entry) > 6 else ""   # status
            ))
    
    def send_bulk_reminders(self):
        """Send bulk reminders for tomorrow's appointments"""
        try:
            cur = self.app.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if not cur.fetchone():
                messagebox.showinfo("Info", "Enhanced appointments not available")
                return
            
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT COUNT(*) FROM appointments_enhanced 
                WHERE appointment_date = ? 
                AND status = 'SCHEDULED'
                AND reminder_sent = 0
            """, (tomorrow,))
            
            count = cur.fetchone()[0]
            
            if count == 0:
                messagebox.showinfo("Info", "No appointments need reminders for tomorrow")
                return
            
            result = messagebox.askyesno("Confirm", 
                                       f"Send reminders for {count} appointment(s) tomorrow?")
            
            if result:
                sent_count = 0
                cur.execute("""
                    SELECT appointment_id FROM appointments_enhanced 
                    WHERE appointment_date = ? 
                    AND status = 'SCHEDULED'
                    AND reminder_sent = 0
                """, (tomorrow,))
                
                appointments = cur.fetchall()
                
                for apt in appointments:
                    if self.app.communication_manager.send_appointment_reminder(apt[0]):
                        sent_count += 1
                
                messagebox.showinfo("Success", f"Sent {sent_count} reminder(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send reminders: {str(e)}")
    
    def send_bulk_followups(self):
        """Send bulk follow-ups for completed appointments"""
        try:
            cur = self.app.db.cursor()
            
            # Check if enhanced table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments_enhanced'")
            if not cur.fetchone():
                messagebox.showinfo("Info", "Enhanced appointments not available")
                return
            
            # Get appointments completed yesterday
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT COUNT(*) FROM appointments_enhanced 
                WHERE appointment_date = ? 
                AND status = 'COMPLETED'
                AND follow_up_needed = 1
            """, (yesterday,))
            
            count = cur.fetchone()[0]
            
            if count == 0:
                messagebox.showinfo("Info", "No completed appointments need follow-up from yesterday")
                return
            
            result = messagebox.askyesno("Confirm", 
                                       f"Send follow-ups for {count} completed appointment(s)?")
            
            if result:
                sent_count = 0
                cur.execute("""
                    SELECT appointment_id FROM appointments_enhanced 
                    WHERE appointment_date = ? 
                    AND status = 'COMPLETED'
                    AND follow_up_needed = 1
                """, (yesterday,))
                
                appointments = cur.fetchall()
                
                for apt in appointments:
                    message = "Thank you for visiting our clinic yesterday. How is your pet doing?"
                    if self.app.communication_manager.send_follow_up(apt[0], message):
                        sent_count += 1
                
                messagebox.showinfo("Success", f"Sent {sent_count} follow-up(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send follow-ups: {str(e)}")