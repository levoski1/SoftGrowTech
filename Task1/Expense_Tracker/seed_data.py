"""
seed_data.py
-------------
Populate the expense tracker with sample data for testing and demonstration.

Run this once to get a feel for the app with real-looking data:
  python seed_data.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from expense_tracker import add_expense

SAMPLE_EXPENSES = [
    # (amount, category, description, date)
    (4500,   "Food & Dining",        "Lunch at Mr. Biggs",           "2025-03-01"),
    (850,    "Transportation",       "Bolt ride to Victoria Island",  "2025-03-02"),
    (15000,  "Housing & Utilities",  "Electricity token (EKEDC)",     "2025-03-03"),
    (2200,   "Food & Dining",        "Groceries – Shoprite",          "2025-03-05"),
    (1200,   "Personal Care",        "Haircut at the barber",         "2025-03-06"),
    (5000,   "Entertainment",        "Cinema – premium ticket",       "2025-03-08"),
    (3500,   "Transportation",       "Uber – airport pickup",         "2025-03-10"),
    (8000,   "Healthcare",           "Pharmacy – prescription",       "2025-03-12"),
    (1750,   "Food & Dining",        "Suya at the roadside",          "2025-03-14"),
    (25000,  "Shopping",             "New sneakers",                  "2025-03-15"),
    (500,    "Transportation",       "Bus fare",                      "2025-03-17"),
    (6000,   "Education",            "Online course subscription",    "2025-03-18"),
    (3000,   "Food & Dining",        "Birthday dinner",               "2025-03-20"),
    (12000,  "Housing & Utilities",  "Internet bill (Spectranet)",    "2025-03-21"),
    (900,    "Personal Care",        "Soap and toiletries",           "2025-03-22"),
    (4200,   "Entertainment",        "Streaming subscriptions",       "2025-02-05"),
    (18500,  "Shopping",             "Clothing – Balogun market",     "2025-02-10"),
    (7500,   "Healthcare",           "Doctor consultation",           "2025-02-14"),
    (2800,   "Food & Dining",        "Valentine's day dinner",        "2025-02-14"),
    (1100,   "Transportation",       "Okada to the market",           "2025-02-20"),
]


if __name__ == "__main__":
    print("🌱 Seeding sample expense data...")
    for amount, category, description, date in SAMPLE_EXPENSES:
        expense = add_expense(amount, category, description, date)
        print(f"  ✓ Added [{expense['id']}] ₦{amount:,.0f} – {description}")
    print(f"\n✅ Done! {len(SAMPLE_EXPENSES)} sample expenses added.")
    print("   Run  python main.py  to explore the app.")
