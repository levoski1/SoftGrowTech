"""
analytics.py
------------
Generates summaries and analytics from expense data.

WHY A SEPARATE ANALYTICS MODULE?
  Analytics logic is distinct from CRUD logic. Keeping them separate
  means you can later swap in a charting library or export to Excel
  without touching the core expense logic.
"""

from collections import defaultdict   # dict that auto-initialises missing keys
from expense_tracker import get_all_expenses, filter_expenses


def get_summary(expenses: list[dict] = None) -> dict:
    """
    Calculate overall summary statistics for a list of expenses.

    Args:
        expenses (list[dict]): Expenses to summarise. Defaults to ALL expenses.

    Returns:
        dict: Contains total, count, average, highest, and lowest expense.
    """
    if expenses is None:
        expenses = get_all_expenses()

    if not expenses:
        # Return zeroed-out structure so callers don't need to handle None
        return {
            "total": 0.0,
            "count": 0,
            "average": 0.0,
            "highest": None,
            "lowest": None,
        }

    amounts = [e["amount"] for e in expenses]

    return {
        "total": round(sum(amounts), 2),
        "count": len(amounts),
        "average": round(sum(amounts) / len(amounts), 2),
        # max() and min() with key= lets us find the whole expense dict, not just the amount
        "highest": max(expenses, key=lambda e: e["amount"]),
        "lowest": min(expenses, key=lambda e: e["amount"]),
    }


def get_category_breakdown(expenses: list[dict] = None) -> list[dict]:
    """
    Group expenses by category and calculate totals and percentages.

    WHY defaultdict?
      defaultdict(float) automatically creates a key with value 0.0
      the first time we access it — no need to check if the key exists first.

    Args:
        expenses (list[dict]): Expenses to analyse. Defaults to all.

    Returns:
        list[dict]: Categories sorted by total spend (highest first), with:
                    category, total, count, percentage.
    """
    if expenses is None:
        expenses = get_all_expenses()

    # Accumulate totals and counts per category
    totals = defaultdict(float)
    counts = defaultdict(int)

    for expense in expenses:
        cat = expense["category"]
        totals[cat] += expense["amount"]
        counts[cat] += 1

    overall_total = sum(totals.values())

    # Build result list with percentage for each category
    breakdown = []
    for cat, total in totals.items():
        breakdown.append({
            "category": cat,
            "total": round(total, 2),
            "count": counts[cat],
            # Avoid division by zero if total is 0
            "percentage": round((total / overall_total * 100), 1) if overall_total else 0,
        })

    # Sort by total descending (biggest spender first)
    return sorted(breakdown, key=lambda x: x["total"], reverse=True)


def get_monthly_summary(year: str = None) -> list[dict]:
    """
    Show total spending per month (optionally filtered to a specific year).

    Args:
        year (str): Optional "YYYY" to restrict to one year.

    Returns:
        list[dict]: List of {month, total, count} sorted by month.
    """
    expenses = filter_expenses(year=year) if year else get_all_expenses()

    # Group by "YYYY-MM" (first 7 chars of "YYYY-MM-DD")
    monthly = defaultdict(float)
    counts = defaultdict(int)

    for expense in expenses:
        month_key = expense["date"][:7]   # e.g., "2025-03"
        monthly[month_key] += expense["amount"]
        counts[month_key] += 1

    # Build and sort result list
    result = [
        {
            "month": month,
            "total": round(total, 2),
            "count": counts[month],
        }
        for month, total in monthly.items()
    ]

    return sorted(result, key=lambda x: x["month"])


def get_budget_status(budget: float, month: str, year: str) -> dict:
    """
    Compare actual spending to a given budget for a specific month.

    Args:
        budget (float): The spending limit to compare against.
        month  (str):   Month as "MM".
        year   (str):   Year as "YYYY".

    Returns:
        dict: Actual spend, remaining budget, % used, and over/under status.
    """
    expenses = filter_expenses(month=month, year=year)
    summary = get_summary(expenses)
    spent = summary["total"]

    remaining = round(budget - spent, 2)
    percent_used = round((spent / budget * 100), 1) if budget else 0

    return {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percent_used": percent_used,
        "over_budget": spent > budget,
        "month": f"{year}-{month}",
    }
