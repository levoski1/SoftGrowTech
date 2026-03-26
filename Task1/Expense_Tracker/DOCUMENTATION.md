# 📚 Personal Expense Tracker — Full Project Documentation & Learning Guide

> **Audience:** Python beginners transitioning to intermediate level.
> **Goal:** Understand not just *what* the code does, but *why* each decision was made.

---

## 🗺️ Table of Contents

1. [Project Overview](#1-project-overview)
2. [Real-World Problem Solved](#2-real-world-problem-solved)
3. [Step-by-Step Roadmap](#3-step-by-step-roadmap)
4. [Task 1 — Project Setup & Data Model](#task-1--project-setup--data-model)
5. [Task 2 — Core CRUD Operations](#task-2--core-crud-operations)
6. [Task 3 — Input Validation](#task-3--input-validation)
7. [Task 4 — Display & Terminal UI](#task-4--display--terminal-ui)
8. [Task 5 — Analytics & Reports](#task-5--analytics--reports)
9. [Task 6 — Search & Filtering](#task-6--search--filtering)
10. [Task 7 — Export to CSV](#task-7--export-to-csv)
11. [Task 8 — Main Menu & Application Loop](#task-8--main-menu--application-loop)
12. [Best Practices Applied](#best-practices-applied)
13. [Key Python Concepts Explained](#key-python-concepts-explained)
14. [Optional Improvements](#optional-improvements)

---

## 1. Project Overview

The **Personal Expense Tracker** is a fully functional command-line application that allows users to:

- Record daily expenses with an amount, category, description, and date
- View all their expenses in a clear, colour-coded table
- Search, filter, and slice their expense data in multiple ways
- See analytics: total spend, category breakdown, monthly trend
- Check whether they are within a monthly budget
- Export their data to a CSV file for use in Excel or Google Sheets

All data is stored locally in a `data/expenses.json` file. No internet connection, no database server, and no third-party libraries are required.

---

## 2. Real-World Problem Solved

Most people have no clear picture of where their money goes. This app provides that picture in minutes. By the end of this project, you will have built a tool that you can actually use every day.

In professional terms, this project teaches you to build a **CRUD application** with **data persistence**, **input validation**, **analytics**, and a **clean separation of concerns** — all core skills for any software engineering role.

---

## 3. Step-by-Step Roadmap

The project is broken into 8 tasks, each building on the last. You could tackle one task per day as a daily challenge.

| Task | Focus | Files Touched |
|------|-------|---------------|
| Task 1 | Setup & data model | `expense_tracker.py` (load/save) |
| Task 2 | CRUD operations | `expense_tracker.py` (add/get/update/delete) |
| Task 3 | Input validation | `utils/validators.py` |
| Task 4 | Terminal display & UI | `utils/display.py` |
| Task 5 | Analytics & reports | `reports/analytics.py` |
| Task 6 | Search & filtering | `expense_tracker.py` (filter/search) |
| Task 7 | CSV export | `utils/export.py` |
| Task 8 | Main menu loop | `main.py` |

---

## Task 1 — Project Setup & Data Model

### Goal
Decide how expenses will be stored and create functions to load and save them.

### Why JSON?
JSON is human-readable (you can open `expenses.json` in any text editor), natively supported by Python, and a great stepping stone before using a real database. For small datasets (< 10,000 records), it performs fine.

### The Data Model

Each expense is a Python dictionary with these keys:

```python
{
    "id":          "a3f19c2b",          # Unique 8-char ID
    "amount":      4500.0,              # Always a float
    "category":    "Food & Dining",     # One of 10 fixed categories
    "description": "Lunch at Mr. Biggs",
    "date":        "2025-03-25",        # ISO 8601 — sortable, universal
    "created_at":  "2025-03-25T14:30:00.123456"  # Full timestamp
}
```

**Why ISO dates (`YYYY-MM-DD`)?**
This format sorts alphabetically in the correct chronological order. `"2025-03-25" > "2025-02-10"` is both alphabetically and chronologically true — a very useful property.

### Key Code

```python
def load_expenses() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []                              # No crash on first run
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_expenses(expenses: list[dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=4)      # indent=4 = human-readable
```

**Why `exist_ok=True`?**
This tells `os.makedirs` not to raise an error if the directory already exists. Without it, the second run of the app would crash when trying to create a `data/` folder that's already there.

---

## Task 2 — Core CRUD Operations

### Goal
Implement the four fundamental data operations: **C**reate, **R**ead, **U**pdate, **D**elete.

### Adding an Expense

```python
def add_expense(amount, category, description, date=None):
    expenses = load_expenses()
    expense = {
        "id": str(uuid.uuid4())[:8],          # Unique short ID
        "amount": round(float(amount), 2),
        ...
    }
    expenses.append(expense)
    save_expenses(expenses)
    return expense
```

**Why `uuid`?**
`uuid.uuid4()` generates a random, universally unique identifier. The chance of two IDs being the same is astronomically small. We only use 8 characters to keep it readable.

**Why `round(float(amount), 2)`?**
Floating-point arithmetic in computers is imprecise. `0.1 + 0.2` in Python is `0.30000000000000004`. Rounding to 2 decimal places avoids displaying nonsense values like `₦1500.00000001`.

### Updating with `**kwargs`

```python
def update_expense(expense_id, **kwargs):
    for expense in expenses:
        if expense["id"] == expense_id:
            for key, value in kwargs.items():
                expense[key] = value
```

`**kwargs` (keyword arguments) lets the caller pass only the fields they want to update:

```python
update_expense("a3f19c2b", amount=5000)           # Only updates amount
update_expense("a3f19c2b", description="Dinner")  # Only updates description
```

This is far more flexible than requiring all fields every time.

---

## Task 3 — Input Validation

### Goal
Ensure all data entering the system is clean and sensible before saving it.

### The Validation Pattern

Every validator returns a tuple: `(value_or_None, error_or_None)`.

```python
def validate_amount(amount_str):
    try:
        value = float(amount_str.replace(",", "").strip())
        if value <= 0:
            return None, "Amount must be greater than zero."
        return round(value, 2), None   # Success: value, no error
    except ValueError:
        return None, "Please enter a valid number."
```

**Why return a tuple instead of raising an exception?**
Exceptions are for unexpected, exceptional errors. Invalid user input is *expected* — users mistype things all the time. Returning `(None, "error message")` is cleaner for validation because it keeps control flow in the calling function.

### Date Validation

```python
def validate_date(date_str):
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        if parsed.date() > datetime.now().date():
            return None, "Date cannot be in the future."
        return parsed.strftime("%Y-%m-%d"), None
    except ValueError:
        return None, "Date must be in YYYY-MM-DD format."
```

`datetime.strptime` raises `ValueError` if the string doesn't match the format exactly — we catch that to give a helpful message instead of a traceback.

---

## Task 4 — Display & Terminal UI

### Goal
Make the terminal output readable, colour-coded, and user-friendly.

### ANSI Colour Codes

ANSI escape codes are special character sequences that terminals interpret as formatting instructions — no library needed.

```python
class Color:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    CYAN   = "\033[94m"
    RESET  = "\033[0m"    # Returns to default colour

def colored(text, color):
    return f"{color}{text}{Color.RESET}"
```

Usage: `print(colored("₦5,000.00", Color.GREEN))` prints green text.

### Text-Based Bar Charts

```python
bar_len = int((item["percentage"] / 100) * 30)   # Scale to max 30 chars
bar = "█" * bar_len
print(f"{item['category']:<22}  {bar}  {item['percentage']}%")
```

By using the `█` block character repeated N times, we get a visual bar chart entirely in plain text. No `matplotlib` required.

---

## Task 5 — Analytics & Reports

### Goal
Derive meaningful insights from the raw expense data.

### Category Breakdown with `defaultdict`

```python
from collections import defaultdict

totals = defaultdict(float)   # auto-creates key with value 0.0

for expense in expenses:
    totals[expense["category"]] += expense["amount"]
```

`defaultdict(float)` automatically initialises any new key to `0.0`. Compare with a regular dict:

```python
# Regular dict — crashes if key doesn't exist
totals["Food"] += 500    # KeyError!

# With defaultdict — works perfectly
totals["Food"] += 500    # Creates "Food": 0.0 first, then adds 500
```

### Summary Statistics

```python
amounts = [e["amount"] for e in expenses]   # List comprehension

summary = {
    "total":   round(sum(amounts), 2),
    "average": round(sum(amounts) / len(amounts), 2),
    "highest": max(expenses, key=lambda e: e["amount"]),
}
```

`max(expenses, key=lambda e: e["amount"])` finds the entire expense dictionary with the highest amount, not just the amount itself. The `key=` argument tells `max()` what to compare.

---

## Task 6 — Search & Filtering

### Goal
Let users find specific expenses without scrolling through everything.

### Composable Filters

```python
def filter_expenses(category=None, month=None, year=None, min_amount=None, max_amount=None):
    expenses = get_all_expenses()

    if category:
        expenses = [e for e in expenses if e["category"] == category]
    if month:
        expenses = [e for e in expenses if f"-{month}-" in e["date"]]
    ...
    return expenses
```

Each filter is applied only if it was provided (not `None`). This lets you combine filters freely:

```python
filter_expenses(category="Food & Dining", year="2025")  # Both filters active
filter_expenses(month="03")                              # Only month filter
```

### Keyword Search

```python
def search_expenses(keyword):
    keyword = keyword.lower()
    return [
        e for e in get_all_expenses()
        if keyword in e["description"].lower()
        or keyword in e["category"].lower()
    ]
```

Converting both sides to lowercase with `.lower()` makes the search case-insensitive. Searching "food" will match "Food & Dining" and "food stall" and "Junk Food".

---

## Task 7 — Export to CSV

### Goal
Allow users to take their data out of the app and into a spreadsheet.

```python
import csv

fieldnames = ["id", "date", "amount", "category", "description", "created_at"]

with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(expenses)
```

`csv.DictWriter` takes a list of dicts and writes each as a CSV row, matching dictionary keys to column headers. `extrasaction="ignore"` means extra keys in the dict (like `updated_at`) are silently skipped.

---

## Task 8 — Main Menu & Application Loop

### Goal
Tie everything together with a clear, navigable menu.

### The Main Loop Pattern

```python
def main():
    while True:
        print_menu(...)
        choice = int(input("Choose: ")) - 1

        if choice == EXIT_OPTION:
            sys.exit(0)

        handler = handlers.get(choice)
        if handler:
            handler()
```

**Why `while True`?**
The menu should keep appearing after each action until the user explicitly exits. `while True` creates an infinite loop that we only break out of when the user chooses "Exit" (via `sys.exit()`).

**Why a `handlers` dictionary?**

```python
handlers = {
    0: add_expense_flow,
    1: view_expenses_flow,
    ...
}
handler = handlers.get(choice)
if handler:
    handler()
```

Using a dictionary to map numbers to functions is cleaner than a long `if/elif` chain and makes it trivial to add new menu options.

---

## Best Practices Applied

### 1. Single Responsibility Principle
Each module does one thing:
- `expense_tracker.py` → data only
- `display.py` → UI only
- `analytics.py` → calculations only

### 2. DRY (Don't Repeat Yourself)
Reusable helpers like `format_amount()`, `colored()`, and `prompt()` are written once and used everywhere.

### 3. Type Hints
```python
def add_expense(amount: float, category: str, description: str, date: str = None) -> dict:
```
Type hints document what each function expects and returns. They don't enforce types at runtime but are invaluable for readability and IDE support.

### 4. Docstrings
Every function has a docstring explaining its purpose, arguments, and return value. This is professional-grade documentation.

### 5. Guard Clause / Early Return
```python
if not expenses:
    return {"total": 0.0, ...}   # Return early, avoid deep nesting
```

Returning early for edge cases (empty lists, missing IDs) keeps the main logic clean and avoids deeply nested `if` blocks.

---

## Key Python Concepts Explained

| Concept | Where You See It | Why It Matters |
|---|---|---|
| `f-strings` | Everywhere | Cleaner string formatting than `%` or `.format()` |
| List comprehensions | Filtering, searching | Concise way to create filtered lists |
| `defaultdict` | analytics.py | Auto-initialise dict keys, no `KeyError` |
| `json.load/dump` | expense_tracker.py | Python ↔ JSON serialisation |
| `*args / **kwargs` | `update_expense` | Flexible function signatures |
| `lambda` | Sorting, max/min | Inline anonymous functions |
| `datetime.strptime` | validators.py | Parse strings into datetime objects |
| `uuid.uuid4()` | expense_tracker.py | Generate unique IDs |
| `os.path.exists` | load_expenses | Safe file access |
| `sys.exit()` | main.py | Clean application shutdown |
| ANSI codes | display.py | Terminal colour without libraries |
| `csv.DictWriter` | export.py | Write dicts as CSV rows |

---

## Optional Improvements

### 1. SQLite Database (Intermediate)
Replace the JSON file with an SQLite database using Python's built-in `sqlite3` module. This gives you proper indexing, transactions, and the ability to query with SQL.

```python
import sqlite3
conn = sqlite3.connect("data/expenses.db")
conn.execute("CREATE TABLE IF NOT EXISTS expenses (...)")
```

### 2. Matplotlib Charts (Intermediate)
```bash
pip install matplotlib
```
```python
import matplotlib.pyplot as plt
plt.bar(categories, totals)
plt.title("Spending by Category")
plt.show()
```

### 3. Flask Web Interface (Advanced)
Convert the CLI into a web app where you can add and view expenses in a browser.

```bash
pip install flask
```
```python
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", expenses=get_all_expenses())
```

### 4. Recurring Expenses (Intermediate)
Add a `recurring` field to expenses and a daily script that auto-adds them at the start of each month using Python's `schedule` library.

### 5. Budget Alerts (Beginner-Intermediate)
Check after every `add_expense()` call if the monthly total has crossed a threshold and print a warning automatically.

---

*This documentation was designed to grow with you. Re-read it as you gain more experience — you'll find new layers of meaning each time.*
