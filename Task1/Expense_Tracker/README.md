# 💰 Personal Expense Tracker

> A beginner-to-intermediate Python CLI application to track, categorise, and analyse your personal spending — with no external libraries required.

---

## 📌 Project Description

The Personal Expense Tracker is a command-line application that helps you record daily expenses, organise them by category, and gain insight into your spending habits through summaries and visual text charts.

It stores data locally in a JSON file and is built using only Python's standard library, making it easy to understand, modify, and extend.

---

## ✨ Features

| Feature | Description |
|---|---|
| ➕ Add Expense | Record amount, category, description, and date |
| 📋 View All | See all expenses in a formatted, colour-coded table |
| 🔍 Search & Filter | Search by keyword or filter by category, month, year, or amount range |
| ✏️ Edit | Update any field of an existing expense |
| 🗑️ Delete | Remove an expense (with confirmation) |
| 📊 Analytics | Summary stats, spending by category, monthly overview, and budget checker |
| 💾 Export | Export filtered or all expenses to CSV |
| 🌈 Coloured UI | ANSI colour-coded terminal output (no extra libraries needed) |

---

## 🗂️ Folder Structure

```
expense_tracker/
│
├── main.py                  # Entry point — menus and user interaction
├── expense_tracker.py       # Core logic — CRUD operations and data layer
├── seed_data.py             # Optional: populate app with sample data
│
├── data/
│   └── expenses.json        # Auto-created — stores all expense records
│
├── reports/
│   ├── __init__.py
│   └── analytics.py         # Summary, category breakdown, monthly charts, budget
│
└── utils/
    ├── __init__.py
    ├── display.py           # Terminal UI — colours, tables, menus, prompts
    ├── validators.py        # Input validation — amounts, dates, descriptions
    └── export.py            # CSV export utility
```

---

## ⚙️ Installation

**Requirements:** Python 3.10 or higher (no external packages needed).

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/expense-tracker.git
cd expense-tracker

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# No pip install needed — only standard library used!
```

---

## ▶️ How to Run

```bash
# Start the application
python main.py

# (Optional) Seed sample Nigerian expense data for testing
python seed_data.py
```

---

## 📖 Example Usage

### Adding an Expense

```
▶ Amount: 4500
▶ Category: 1  (Food & Dining)
▶ Description: Lunch at the canteen
▶ Date [2025-03-25]:

  Review your entry:
  Amount:      ₦4,500.00
  Category:    Food & Dining
  Description: Lunch at the canteen
  Date:        2025-03-25

▶ Save this expense? (y/n): y
  ✓ Expense saved! (ID: a3f19c2b)
```

### Viewing Expenses

```
══════════════════════════════════════════════════════════
                        All Expenses
══════════════════════════════════════════════════════════
      ID          Date          Amount          Category                Description
──────────────────────────────────────────────────────────
1.    a3f19c2b    2025-03-25    ₦4,500.00       Food & Dining           Lunch at the canteen
2.    b7e30d11    2025-03-22    ₦850.00         Transportation          Bolt ride
──────────────────────────────────────────────────────────
                                          Total:  ₦5,350.00
```

### Category Chart

```
══════════════════════════════════
     Spending by Category
══════════════════════════════════
  Food & Dining         ██████████████████████████    ₦10,450.00    38.5%
  Transportation        ████████                      ₦3,150.00     11.6%
  Housing & Utilities   ██████████████████            ₦27,000.00    ...
```

---

## 🧱 Key Concepts Used

| Concept | Where Used |
|---|---|
| Functions | All modules — each operation is a named function |
| File I/O | `expense_tracker.py` — reading/writing JSON |
| JSON | Data persistence in `data/expenses.json` |
| Dictionaries | Each expense is a Python `dict` |
| List comprehensions | Filtering and searching expenses |
| `datetime` module | Date validation, formatting, default values |
| `uuid` module | Generating unique expense IDs |
| `csv` module | Exporting data |
| ANSI escape codes | Terminal colour output |
| Modular design | Logic, display, validation, and analytics are separated |
| `defaultdict` | Accumulating category/monthly totals |
| `**kwargs` | Flexible field updates in `update_expense()` |

---

## 🔮 Future Improvements

| Improvement | How to Implement |
|---|---|
| SQLite database | Replace JSON with `sqlite3` for faster queries and larger datasets |
| Charts with matplotlib | `pip install matplotlib` and use `plt.bar()` for visual graphs |
| Budget alerts | Notify when monthly spending exceeds a set limit |
| Recurring expenses | Auto-add fixed expenses (rent, subscriptions) monthly |
| Web UI | Use Flask or FastAPI to serve a browser-based interface |
| Multi-user support | Add user authentication with `bcrypt` password hashing |
| Mobile app | Expose a REST API that a React Native app can consume |

---

## 👨‍💻 Author

Built as a structured learning project for beginner-to-intermediate Python developers.

**License:** MIT — free to use, modify, and share.
