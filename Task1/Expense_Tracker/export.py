"""
utils/export.py
----------------
Export expenses to CSV format for use in spreadsheet tools.

WHY CSV?
  CSV (Comma-Separated Values) is a universal format that Excel,
  Google Sheets, and almost every data tool can read. It's a great
  way to let users take their data out of the app.
"""

import csv
import os
from datetime import datetime
from expense_tracker import get_all_expenses, filter_expenses


def export_to_csv(
    filename: str = None,
    category: str = None,
    month: str = None,
    year: str = None,
) -> str:
    """
    Export expenses to a CSV file.

    Args:
        filename (str):   Output filename. Defaults to a timestamped name.
        category (str):   Optional category filter.
        month    (str):   Optional month filter ("MM").
        year     (str):   Optional year filter ("YYYY").

    Returns:
        str: The path to the exported file.
    """
    # Generate a default filename with the current timestamp
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_export_{timestamp}.csv"

    # Ensure the output file goes to the data/ directory
    filepath = os.path.join("data", filename)
    os.makedirs("data", exist_ok=True)

    # Fetch the relevant expenses
    if any([category, month, year]):
        expenses = filter_expenses(category=category, month=month, year=year)
    else:
        expenses = get_all_expenses()

    # Define which columns to include and in what order
    fieldnames = ["id", "date", "amount", "category", "description", "created_at"]

    # csv.DictWriter writes a dict as a row, matching keys to column headers
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()          # Write the column header row
        writer.writerows(expenses)    # Write all expense rows

    return filepath
