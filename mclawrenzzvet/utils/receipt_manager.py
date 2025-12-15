from datetime import datetime

class ReceiptManager:
    """Manages receipt generation and printing"""
    @staticmethod
    def generate_receipt_text(appointment_id, patient_name, owner_name, animal_type, notes, date, total_amount, cart_items):
        """Generate receipt as text string"""
        receipt = "=" * 50 + "\n"
        receipt += "         VETERINARY CLINIC\n"
        receipt += "       Official Service Receipt\n"
        receipt += "   123 Main Street, City, Philippines\n"
        receipt += "          Tel: (02) 1234-5678\n"
        receipt += "=" * 50 + "\n\n"

        receipt += f"Appointment: {appointment_id}\n"
        receipt += f"Date: {date}\n"
        receipt += f"Patient: {patient_name}\n"
        receipt += f"Owner: {owner_name}\n"
        receipt += f"Animal Type: {animal_type}\n"
        if notes:
            receipt += f"Notes: {notes}\n"
        receipt += "\n" + "-" * 50 + "\n"
        receipt += "SERVICE/ITEM                       QTY   PRICE   SUBTOTAL\n"
        receipt += "-" * 50 + "\n"

        for item in cart_items:
            item_name = item['name']
            if len(item_name) > 30:
                item_name = item_name[:27] + "..."

            receipt += f"{item_name:<30} {item['qty']:>3}  ₱{item['price']:>6.2f}  ₱{item['subtotal']:>7.2f}\n"

        receipt += "-" * 50 + "\n"
        receipt += f"TOTAL: ₱{total_amount:>38.2f}\n"
        receipt += "=" * 50 + "\n\n"

        receipt += "POLICY:\n"
        receipt += "• Follow-up appointments as advised\n"
        receipt += "• Keep this receipt for records\n"
        receipt += "• Contact us for any concerns\n\n"

        receipt += "Thank you for choosing our clinic!\n"
        receipt += "We care for your pets\n"
        receipt += "=" * 50 + "\n"

        return receipt

    @staticmethod
    def save_receipt_to_file(receipt_text, filename=None):
        """Save receipt to text file"""
        if filename is None:
            filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            return filename
        except Exception as e:
            print(f"Error saving receipt: {e}")
            return None