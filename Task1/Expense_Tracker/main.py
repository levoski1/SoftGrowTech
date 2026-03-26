"""
main.py
--------
Entry point for the Personal Expense Tracker application.

This file handles all user interaction (menus, prompts, confirmations)
and delegates actual logic to expense_tracker.py, analytics.py,
display.py, validators.py, and export.py. This follows the MVC pattern (Model-View-Controller):

  Model      → expense_tracker.py (data & logic)
    View       → display.py         (formatting & output)
  Controller → main.py            (ties user input to model actions)

HOW TO RUN:
  python main.py
"""

import sys
import os
from datetime import datetime

# Add project root to path so imports work when run from any directory
sys.path.insert(0, os.path.dirname(__file__))

# ── Local imports ──────────────────────────────────────────────────────────────
import expense_tracker as et
from analytics import (
    get_summary,
    get_category_breakdown,
    get_monthly_summary,
    get_budget_status,
)
from display import (
    Color, colored, bold, header, divider,
    print_expense_table, print_category_chart, print_monthly_chart,
    prompt, prompt_float, prompt_choice, confirm,
    success, error, info, format_amount,
)
from validators import validate_amount, validate_date, validate_description
from export import export_to_csv
from dashboard import generate_dashboard_report


# ─── MAIN MENU ────────────────────────────────────────────────────────────────

MAIN_MENU = [
    "➕  Add Expense",
    "📋  View All Expenses",
    "🔍  Search & Filter",
    "✏️   Edit Expense",
    "🗑️   Delete Expense",
    "📊  Analytics & Reports",
    "💾  Export to CSV",
    "🌐  Open Dashboard",
    "❌  Exit",
]


def show_welcome() -> None:
    """Display the welcome banner on startup."""
    print("\n")
    print(colored("╔══════════════════════════════════════════════════════════╗", Color.CYAN))
    print(colored("║         💰  PERSONAL EXPENSE TRACKER  💰                 ║", Color.CYAN))
    print(colored("║         Track. Analyse. Save.                            ║", Color.DIM))
    print(colored("╚══════════════════════════════════════════════════════════╝", Color.CYAN))
    print()

    # Show a quick summary on launch so the user is immediately oriented
    expenses = et.get_all_expenses()
    summary = get_summary(expenses)

    if summary["count"] > 0:
        current_month = datetime.now().strftime("%B %Y")
        print(f"  {bold('This session:')} {summary['count']} expense(s) on record")
        print(f"  {bold('Total tracked:')} {colored(format_amount(summary['total']), Color.GREEN)}")
    else:
        print(colored("  No expenses yet. Add your first one to get started!", Color.YELLOW))
    print()


# ─── FEATURE: ADD EXPENSE ─────────────────────────────────────────────────────

def add_expense_flow() -> None:
    """
    Guide the user through adding a new expense step by step.

    Each field is validated before moving on. If validation fails,
    the user is asked to try again.
    """
    print(header("Add New Expense"))

    # ── Amount ───────────────────────────────────────────────────────────────
    while True:
        raw = prompt("Amount (e.g., 1500 or 99.99)")
        amount, err = validate_amount(raw)
        if err:
            error(err)
        else:
            break

    # ── Category ─────────────────────────────────────────────────────────────
    print(f"\n  {bold('Select a category:')}")
    for i, cat in enumerate(et.CATEGORIES, start=1):
        print(f"  {colored(str(i) + '.', Color.CYAN)}  {cat}")
    print()

    while True:
        try:
            choice = int(prompt("Category number"))
            if 1 <= choice <= len(et.CATEGORIES):
                category = et.CATEGORIES[choice - 1]
                break
            error(f"Please enter a number between 1 and {len(et.CATEGORIES)}.")
        except ValueError:
            error("Please enter a number.")

    # ── Description ───────────────────────────────────────────────────────────
    while True:
        raw = prompt("Description (short note about this expense)")
        desc, err = validate_description(raw)
        if err:
            error(err)
        else:
            break

    # ── Date ──────────────────────────────────────────────────────────────────
    today = datetime.now().strftime("%Y-%m-%d")
    raw = prompt("Date (YYYY-MM-DD)", default=today)

    if raw == today:
        date = today
    else:
        date, err = validate_date(raw)
        if err:
            error(f"{err} Using today's date instead.")
            date = today

    # ── Confirm and Save ──────────────────────────────────────────────────────
    print(f"\n  {bold('Review your entry:')}")
    print(f"  Amount:      {colored(format_amount(amount), Color.GREEN)}")
    print(f"  Category:    {colored(category, Color.MAGENTA)}")
    print(f"  Description: {desc}")
    print(f"  Date:        {colored(date, Color.BLUE)}")
    print()

    if confirm("Save this expense?"):
        expense = et.add_expense(amount, category, desc, date)
        success(f"Expense saved! (ID: {expense['id']})")
    else:
        info("Expense discarded.")


# ─── FEATURE: VIEW EXPENSES ───────────────────────────────────────────────────

def view_expenses_flow() -> None:
    """Display all expenses in a formatted table."""
    expenses = et.get_all_expenses()
    print_expense_table(expenses, "All Expenses")

    if expenses:
        summary = get_summary(expenses)
        print(f"  {bold('Count:')} {summary['count']}   "
              f"{bold('Average:')} {format_amount(summary['average'])}")
        print(divider())


# ─── FEATURE: SEARCH & FILTER ─────────────────────────────────────────────────

def search_filter_flow() -> None:
    """Let the user search by keyword or filter by category/month/year."""
    print(header("Search & Filter"))

    options = [
        "Search by keyword",
        "Filter by category",
        "Filter by month",
        "Filter by year",
        "Filter by amount range",
        "← Back to main menu",
    ]

    for i, opt in enumerate(options, start=1):
        print(f"  {colored(str(i) + '.', Color.CYAN)}  {opt}")
    print()

    try:
        choice = int(prompt("Choose filter type"))
    except ValueError:
        error("Invalid choice.")
        return

    if choice == 1:
        keyword = prompt("Enter search keyword")
        results = et.search_expenses(keyword)
        print_expense_table(results, f"Results for '{keyword}'")

    elif choice == 2:
        for i, cat in enumerate(et.CATEGORIES, start=1):
            print(f"  {colored(str(i) + '.', Color.CYAN)}  {cat}")
        try:
            cat_choice = int(prompt("Category number"))
            category = et.CATEGORIES[cat_choice - 1]
            results = et.filter_expenses(category=category)
            print_expense_table(results, f"Category: {category}")
        except (ValueError, IndexError):
            error("Invalid category selection.")

    elif choice == 3:
        month = prompt("Month (MM, e.g., 03 for March)")
        year = prompt("Year (YYYY)", default=str(datetime.now().year))
        results = et.filter_expenses(month=month, year=year)
        print_expense_table(results, f"Expenses for {year}-{month}")

    elif choice == 4:
        year = prompt("Year (YYYY)")
        results = et.filter_expenses(year=year)
        print_expense_table(results, f"Expenses for {year}")

    elif choice == 5:
        try:
            min_a = float(prompt("Minimum amount (press Enter to skip)", default="0"))
            max_a = prompt("Maximum amount (press Enter to skip)")
            max_val = float(max_a) if max_a else None
            results = et.filter_expenses(min_amount=min_a if min_a else None, max_amount=max_val)
            print_expense_table(results, "Filtered by Amount Range")
        except ValueError:
            error("Invalid amount entered.")

    elif choice == 6:
        return


# ─── FEATURE: EDIT EXPENSE ────────────────────────────────────────────────────

def edit_expense_flow() -> None:
    """Let the user edit an existing expense by ID."""
    print(header("Edit Expense"))

    expense_id = prompt("Enter the Expense ID to edit (found in the View screen)")
    expense = et.get_expense_by_id(expense_id)

    if not expense:
        error(f"No expense found with ID '{expense_id}'.")
        return

    # Show the current values
    print(f"\n  {bold('Current values:')}")
    print(f"  Amount:      {format_amount(expense['amount'])}")
    print(f"  Category:    {expense['category']}")
    print(f"  Description: {expense['description']}")
    print(f"  Date:        {expense['date']}")
    print()
    info("Press Enter to keep the current value for any field.")

    updates = {}

    # ── Amount ───────────────────────────────────────────────────────────────
    raw = prompt("New amount", default=str(expense["amount"]))
    if raw != str(expense["amount"]):
        amount, err = validate_amount(raw)
        if err:
            error(err)
        else:
            updates["amount"] = amount

    # ── Category ─────────────────────────────────────────────────────────────
    print(f"\n  Current category: {colored(expense['category'], Color.MAGENTA)}")
    change_cat = confirm("Change category?")
    if change_cat:
        for i, cat in enumerate(et.CATEGORIES, start=1):
            print(f"  {colored(str(i) + '.', Color.CYAN)}  {cat}")
        try:
            cat_choice = int(prompt("New category number"))
            updates["category"] = et.CATEGORIES[cat_choice - 1]
        except (ValueError, IndexError):
            error("Invalid choice. Category unchanged.")

    # ── Description ───────────────────────────────────────────────────────────
    raw = prompt("New description", default=expense["description"])
    if raw != expense["description"]:
        desc, err = validate_description(raw)
        if err:
            error(err)
        else:
            updates["description"] = desc

    # ── Date ──────────────────────────────────────────────────────────────────
    raw = prompt("New date (YYYY-MM-DD)", default=expense["date"])
    if raw != expense["date"]:
        date, err = validate_date(raw)
        if err:
            error(err)
        else:
            updates["date"] = date

    if not updates:
        info("No changes made.")
        return

    if confirm("Save changes?"):
        updated = et.update_expense(expense_id, **updates)
        if updated:
            success("Expense updated successfully!")
        else:
            error("Update failed. Please try again.")
    else:
        info("Edit discarded.")


# ─── FEATURE: DELETE EXPENSE ──────────────────────────────────────────────────

def delete_expense_flow() -> None:
    """Let the user delete an expense by ID, with confirmation."""
    print(header("Delete Expense"))

    expense_id = prompt("Enter the Expense ID to delete")
    expense = et.get_expense_by_id(expense_id)

    if not expense:
        error(f"No expense found with ID '{expense_id}'.")
        return

    print(f"\n  {bold('You are about to delete:')}")
    print(f"  {format_amount(expense['amount'])}  ·  {expense['category']}  ·  {expense['description']}")
    print()

    if confirm(colored("Are you sure? This cannot be undone.", Color.RED)):
        deleted = et.delete_expense(expense_id)
        if deleted:
            success("Expense deleted.")
        else:
            error("Deletion failed.")
    else:
        info("Deletion cancelled.")


# ─── FEATURE: ANALYTICS ───────────────────────────────────────────────────────

def analytics_flow() -> None:
    """Show analytics sub-menu."""
    print(header("Analytics & Reports"))

    options = [
        "Overall summary",
        "Spending by category (chart)",
        "Monthly spending (chart)",
        "Budget checker",
        "← Back",
    ]
    for i, opt in enumerate(options, start=1):
        print(f"  {colored(str(i) + '.', Color.CYAN)}  {opt}")
    print()

    try:
        choice = int(prompt("Choose report"))
    except ValueError:
        return

    if choice == 1:
        expenses = et.get_all_expenses()
        summary = get_summary(expenses)
        print(header("Overall Summary"))
        print(f"  {bold('Total expenses:'):25} {summary['count']}")
        print(f"  {bold('Total amount:'):25} {colored(format_amount(summary['total']), Color.GREEN)}")
        print(f"  {bold('Average per expense:'):25} {format_amount(summary['average'])}")
        if summary["highest"]:
            h = summary["highest"]
            print(f"  {bold('Highest single expense:'):25} {format_amount(h['amount'])} ({h['description']})")
        if summary["lowest"]:
            l = summary["lowest"]
            print(f"  {bold('Lowest single expense:'):25} {format_amount(l['amount'])} ({l['description']})")
        print(divider())

    elif choice == 2:
        breakdown = get_category_breakdown()
        print_category_chart(breakdown)

    elif choice == 3:
        year = prompt("Filter by year (press Enter for all)", default="")
        monthly = get_monthly_summary(year if year else None)
        print_monthly_chart(monthly)

    elif choice == 4:
        try:
            budget = float(prompt("Enter your monthly budget"))
            month = prompt("Month (MM)", default=datetime.now().strftime("%m"))
            year = prompt("Year (YYYY)", default=datetime.now().strftime("%Y"))
            status = get_budget_status(budget, month, year)

            print(header(f"Budget Status — {status['month']}"))
            print(f"  {bold('Budget:'):20} {format_amount(status['budget'])}")
            print(f"  {bold('Spent:'):20} {colored(format_amount(status['spent']), Color.RED if status['over_budget'] else Color.GREEN)}")
            print(f"  {bold('Remaining:'):20} {format_amount(status['remaining'])}")
            print(f"  {bold('% Used:'):20} {status['percent_used']}%")

            if status["over_budget"]:
                print(f"\n  {colored('⚠ You are OVER BUDGET!', Color.RED)}")
            else:
                print(f"\n  {colored('✓ You are within budget.', Color.GREEN)}")
            print(divider())

        except ValueError:
            error("Invalid budget amount.")

    elif choice == 5:
        return


# ─── FEATURE: EXPORT ──────────────────────────────────────────────────────────

def export_flow() -> None:
    """Export expenses to CSV."""
    print(header("Export to CSV"))
    info("Exporting all expenses to CSV...")
    filepath = export_to_csv()
    success(f"Exported to: {os.path.abspath(filepath)}")


def dashboard_flow() -> None:
    """Generate and open a modern HTML dashboard from current data."""
    print(header("Open Dashboard"))
    info("Generating interactive HTML report...")
    report_path = generate_dashboard_report(output_path="report.html", open_browser=True)
    success(f"Dashboard ready: {report_path}")


# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Application main loop.

    Displays the main menu repeatedly until the user chooses to exit.
    Each menu option maps to a dedicated flow function above.

    WHY A LOOP?
      A while True loop is the standard pattern for interactive CLI apps.
      We break out of it only when the user explicitly chooses "Exit".
    """
    show_welcome()

    # Map menu choice index (0-based) to handler function
    handlers = {
        0: add_expense_flow,
        1: view_expenses_flow,
        2: search_filter_flow,
        3: edit_expense_flow,
        4: delete_expense_flow,
        5: analytics_flow,
        6: export_flow,
        7: dashboard_flow,
    }

    while True:
        print(header("Main Menu"))
        for i, option in enumerate(MAIN_MENU, start=1):
            print(f"  {colored(str(i) + '.', Color.CYAN)}  {option}")
        print(divider())

        try:
            raw = prompt("Choose an option")
            choice = int(raw) - 1   # Convert to 0-based index

            if choice == len(MAIN_MENU) - 1:   # Last option = Exit
                print(colored("\n  Goodbye! Keep tracking those expenses 💸\n", Color.CYAN))
                sys.exit(0)

            handler = handlers.get(choice)
            if handler:
                print()
                handler()
            else:
                error(f"Please enter a number between 1 and {len(MAIN_MENU)}.")

        except ValueError:
            error("Please enter a number.")
        except KeyboardInterrupt:
            # Allow Ctrl+C to cleanly exit without a traceback
            print(colored("\n\n  Interrupted. Goodbye!\n", Color.YELLOW))
            sys.exit(0)

        # Pause between actions so the user can read the output
        print()
        input(colored("  Press Enter to continue...", Color.DIM))
        print("\033[2J\033[H")   # Clear the terminal screen


# ── Standard Python entry-point guard ─────────────────────────────────────────
# This ensures main() only runs when the file is executed directly,
# not when it's imported as a module by another file.

if __name__ == "__main__":
    main()
