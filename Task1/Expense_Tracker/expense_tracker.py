"""
expense_tracker.py
------------------
Core module for the Personal Expense Tracker application.
Handles all expense-related logic: adding, viewing, editing,
deleting, and filtering expenses.

WHY A SEPARATE MODULE?
  Separating business logic from the UI (main.py) makes the code
  testable, reusable, and easier to maintain. This is called the
  "Separation of Concerns" principle.
"""

import json           # For reading/writing data to a JSON file
import os             # For checking if the data file exists
import uuid           # For generating unique IDs for each expense
from datetime import datetime   # For timestamping expenses

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
# Keeping magic values as constants makes them easy to find and update

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "expenses.json")   # Where all expense data is stored

# Valid categories the user can choose from
CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Utilities",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]


# ─── DATA LAYER ───────────────────────────────────────────────────────────────
# These functions handle reading from and writing to the JSON file.
# Think of this as your app's mini database layer.

def load_expenses() -> list[dict]:
    """
    Load all expenses from the JSON file.

    Returns an empty list if the file doesn't exist yet.
    This prevents crashes on first run.

    Returns:
        list[dict]: A list of expense dictionaries.
    """
    # If the file doesn't exist yet, return an empty list
    # (this happens on the very first run of the app)
    if not os.path.exists(DATA_FILE):
        return []

    # Open the file and parse the JSON content into a Python list
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_expenses(expenses: list[dict]) -> None:
    """
    Save the full list of expenses to the JSON file.

    WHY OVERWRITE EVERYTHING?
      This is a simple approach for a small dataset. We load all
      expenses, modify the list in memory, then write everything
      back. For large datasets, you'd use a real database instead.

    Args:
        expenses (list[dict]): The full list of expenses to save.
    """
    # Ensure the data/ directory exists before writing
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # Write the list to the file as formatted JSON (indent=4 makes it human-readable)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=4, ensure_ascii=False)


# ─── CRUD OPERATIONS ──────────────────────────────────────────────────────────
# CRUD = Create, Read, Update, Delete — the four basic data operations

def add_expense(amount: float, category: str, description: str, date: str = None) -> dict:
    """
    Create a new expense and save it.

    WHY uuid?
      Every expense needs a unique identifier so we can find and
      delete/edit specific records later, even if two expenses have
      the same amount and category.

    Args:
        amount      (float): How much was spent.
        category    (str):   Which category (e.g., "Food & Dining").
        description (str):   A short note about the expense.
        date        (str):   Optional date string "YYYY-MM-DD". Defaults to today.

    Returns:
        dict: The newly created expense record.
    """
    expenses = load_expenses()

    # Build the expense record as a Python dictionary
    expense = {
        "id": str(uuid.uuid4())[:8],          # Short unique ID (first 8 chars of UUID)
        "amount": round(float(amount), 2),     # Always store as float, rounded to cents
        "category": category,
        "description": description.strip(),    # Remove accidental leading/trailing spaces
        "date": date or datetime.now().strftime("%Y-%m-%d"),  # Default = today
        "created_at": datetime.now().isoformat(),             # Full timestamp for sorting
    }

    expenses.append(expense)   # Add to the list
    save_expenses(expenses)    # Persist to disk
    return expense             # Return so the caller can display a confirmation


def get_all_expenses() -> list[dict]:
    """
    Retrieve all expenses, sorted by date (newest first).

    Returns:
        list[dict]: All expense records.
    """
    expenses = load_expenses()
    # Sort by the 'date' key, reversed so newest appears first
    return sorted(expenses, key=lambda x: x["date"], reverse=True)


def get_expense_by_id(expense_id: str) -> dict | None:
    """
    Find a single expense by its ID.

    Args:
        expense_id (str): The short ID of the expense.

    Returns:
        dict | None: The matching expense, or None if not found.
    """
    expenses = load_expenses()
    # Use next() with a generator — efficient because it stops at first match
    return next((e for e in expenses if e["id"] == expense_id), None)


def update_expense(expense_id: str, **kwargs) -> dict | None:
    """
    Update one or more fields of an existing expense.

    WHY **kwargs?
      Using keyword arguments lets callers update only the fields
      they want to change, without needing to pass all fields every time.
      Example: update_expense("abc12345", amount=50.00)

    Args:
        expense_id (str): The ID of the expense to update.
        **kwargs:         Any fields to update (amount, category, description, date).

    Returns:
        dict | None: The updated expense, or None if not found.
    """
    expenses = load_expenses()

    for expense in expenses:
        if expense["id"] == expense_id:
            # Only update fields that were passed in
            for key, value in kwargs.items():
                if key in ("amount", "category", "description", "date"):
                    # Clean the value the same way we do on creation
                    if key == "amount":
                        expense[key] = round(float(value), 2)
                    elif key == "description":
                        expense[key] = str(value).strip()
                    else:
                        expense[key] = value
            expense["updated_at"] = datetime.now().isoformat()
            save_expenses(expenses)
            return expense

    return None   # Expense not found


def delete_expense(expense_id: str) -> bool:
    """
    Delete an expense by its ID.

    Args:
        expense_id (str): The ID of the expense to remove.

    Returns:
        bool: True if deleted, False if not found.
    """
    expenses = load_expenses()
    original_count = len(expenses)

    # Build a new list that excludes the expense with matching ID
    # This is more Pythonic than finding the index and using del
    updated = [e for e in expenses if e["id"] != expense_id]

    if len(updated) == original_count:
        return False   # Nothing was removed, ID didn't exist

    save_expenses(updated)
    return True


# ─── FILTERING & SEARCH ───────────────────────────────────────────────────────

def filter_expenses(
    category: str = None,
    month: str = None,
    year: str = None,
    min_amount: float = None,
    max_amount: float = None,
) -> list[dict]:
    """
    Filter expenses by one or more criteria.

    All parameters are optional — you can combine them freely.
    Example: filter by category AND month at the same time.

    Args:
        category   (str):   Filter to a specific category.
        month      (str):   Month as "MM" (e.g., "03" for March).
        year       (str):   Year as "YYYY" (e.g., "2025").
        min_amount (float): Minimum expense amount.
        max_amount (float): Maximum expense amount.

    Returns:
        list[dict]: Matching expenses, newest first.
    """
    expenses = get_all_expenses()

    # Apply each filter only if it was provided (not None)
    if category:
        expenses = [e for e in expenses if e["category"] == category]

    if month:
        # Date is stored as "YYYY-MM-DD", so we check if "-MM-" is in it
        expenses = [e for e in expenses if f"-{month}-" in e["date"]]

    if year:
        # Year is the first 4 characters of the date string
        expenses = [e for e in expenses if e["date"].startswith(year)]

    if min_amount is not None:
        expenses = [e for e in expenses if e["amount"] >= min_amount]

    if max_amount is not None:
        expenses = [e for e in expenses if e["amount"] <= max_amount]

    return expenses


def search_expenses(keyword: str) -> list[dict]:
    """
    Search expenses by keyword in the description field.

    Args:
        keyword (str): The search term.

    Returns:
        list[dict]: Matching expenses.
    """
    keyword = keyword.lower().strip()
    expenses = get_all_expenses()
    return [
        e for e in expenses
        if keyword in e["description"].lower() or keyword in e["category"].lower()
    ]
