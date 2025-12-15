"""Initial data population helpers.

This module inserts a curated list of common veterinary medicines into the
`inventory` table if they are not already present. It uses the project's
`database.get_db()` to open the configured SQLite database so it behaves the
same as the application.

The routine is idempotent: running it multiple times will not create
duplicate entries (it checks by `name`).
"""
from datetime import datetime, timedelta
from database import get_db


def _default_expiration(days=365):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def populate_initial_inventory():
    """Insert default medicines into inventory when they're missing.

    This is safe to call multiple times; entries are skipped if an item with
    the same `name` already exists.
    """
    items = [
        {
            "name": "Amoxicillin 250mg",
            "price": 120.00,
            "stock": 50,
            "category": "Antibiotic",
            "image": None,
            "brand": "VetPharm",
            "animal_type": "Dog/Cat",
            "dosage": "250mg",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Carprofen 50mg",
            "price": 200.00,
            "stock": 30,
            "category": "Analgesic",
            "image": None,
            "brand": "PetCare",
            "animal_type": "Dog",
            "dosage": "50mg",
            "expiration_date": _default_expiration(720),
        },
        {
            "name": "Ivermectin 1%",
            "price": 150.00,
            "stock": 40,
            "category": "Antiparasitic",
            "image": None,
            "brand": "AgriVet",
            "animal_type": "Multi",
            "dosage": "1%",
            "expiration_date": _default_expiration(365),
        },
        {
            "name": "Rabies Vaccine (1ml)",
            "price": 450.00,
            "stock": 25,
            "category": "Vaccine",
            "image": None,
            "brand": "SafeVax",
            "animal_type": "Dog/Cat",
            "dosage": "1ml",
            "expiration_date": _default_expiration(300),
        },
        {
            "name": "Dewormer Tablet",
            "price": 80.00,
            "stock": 100,
            "category": "Dewormer",
            "image": None,
            "brand": "CleanPet",
            "animal_type": "Dog/Cat",
            "dosage": "Single",
            "expiration_date": _default_expiration(400),
        },
        {
            "name": "Enrofloxacin 100mg",
            "price": 180.00,
            "stock": 40,
            "category": "Antibiotic",
            "image": None,
            "brand": "BayVet",
            "animal_type": "Dog/Cat",
            "dosage": "100mg",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Metronidazole 250mg",
            "price": 130.00,
            "stock": 60,
            "category": "Antiprotozoal",
            "image": None,
            "brand": "MetroVet",
            "animal_type": "Dog/Cat",
            "dosage": "250mg",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Prednisone 5mg",
            "price": 90.00,
            "stock": 80,
            "category": "Steroid",
            "image": None,
            "brand": "Cortivet",
            "animal_type": "Dog/Cat",
            "dosage": "5mg",
            "expiration_date": _default_expiration(720),
        },
        {
            "name": "Furosemide 20mg",
            "price": 75.00,
            "stock": 50,
            "category": "Diuretic",
            "image": None,
            "brand": "Diurex",
            "animal_type": "Dog",
            "dosage": "20mg",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Cetirizine 10mg",
            "price": 60.00,
            "stock": 100,
            "category": "Antihistamine",
            "image": None,
            "brand": "AllerPet",
            "animal_type": "Dog/Cat",
            "dosage": "10mg",
            "expiration_date": _default_expiration(400),
        },
        {
            "name": "Hydrocortisone Ointment 1%",
            "price": 55.00,
            "stock": 70,
            "category": "Topical",
            "image": None,
            "brand": "Dermapet",
            "animal_type": "Dog/Cat",
            "dosage": "1%",
            "expiration_date": _default_expiration(300),
        },
        {
            "name": "Potassium Supplement 100ml",
            "price": 95.00,
            "stock": 40,
            "category": "Supplement",
            "image": None,
            "brand": "ElectroPet",
            "animal_type": "Dog/Cat",
            "dosage": "100ml",
            "expiration_date": _default_expiration(360),
        },
        {
            "name": "Multivitamin Chewable",
            "price": 120.00,
            "stock": 150,
            "category": "Supplement",
            "image": None,
            "brand": "VitaPet",
            "animal_type": "Dog/Cat",
            "dosage": "Chewable",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Omega-3 Fish Oil 100ml",
            "price": 220.00,
            "stock": 80,
            "category": "Supplement",
            "image": None,
            "brand": "OmegaPet",
            "animal_type": "Dog/Cat",
            "dosage": "100ml",
            "expiration_date": _default_expiration(540),
        },
        {
            "name": "Chlorhexidine Shampoo 250ml",
            "price": 160.00,
            "stock": 60,
            "category": "Antiseptic",
            "image": None,
            "brand": "CleanCoat",
            "animal_type": "Dog/Cat",
            "dosage": "250ml",
            "expiration_date": _default_expiration(480),
        },
    ]

    try:
        conn = get_db()
        cur = conn.cursor()

        # Ensure inventory table exists (init_db should have created it)
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'"
        )
        if not cur.fetchone():
            print("data_catalogs: 'inventory' table does not exist — skipping population")
            conn.close()
            return

        inserted = 0
        for it in items:
            cur.execute("SELECT id FROM inventory WHERE name = ?", (it["name"],))
            if cur.fetchone():
                continue

            cur.execute(
                """
                INSERT INTO inventory
                (name, price, stock, category, image, brand, animal_type, dosage, expiration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    it["name"],
                    it["price"],
                    it["stock"],
                    it["category"],
                    it["image"],
                    it["brand"],
                    it["animal_type"],
                    it["dosage"],
                    it["expiration_date"],
                ),
            )
            inserted += 1

        if inserted > 0:
            conn.commit()
            print(f"data_catalogs: inserted {inserted} default inventory items")
        else:
            print("data_catalogs: default inventory items already present — nothing to do")

        conn.close()

    except Exception as e:
        print(f"data_catalogs: failed to populate inventory: {e}")
