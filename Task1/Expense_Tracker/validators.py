"""
utils/validators.py
--------------------
Input validation functions used throughout the application.

WHY VALIDATE?
  Never trust user input. Validating before saving prevents corrupt
  data, crashes, and confusing errors later. It also gives the user
  helpful, immediate feedback.
"""

import re
from datetime import datetime
from expense_tracker import CATEGORIES


def validate_amount(amount_str: str) -> tuple[float | None, str | None]:
    """
    Validate and parse an amount string.

    Args:
        amount_str (str): Raw user input.

    Returns:
        tuple: (float_value, None) if valid, or (None, error_message) if not.
    """
    try:
        # Remove any currency symbols or commas the user might have typed
        cleaned = amount_str.replace(",", "").replace("₦", "").replace("$", "").strip()
        value = float(cleaned)

        if value <= 0:
            return None, "Amount must be greater than zero."
        if value > 10_000_000:
            return None, "Amount seems unrealistically large. Please double-check."

        return round(value, 2), None

    except ValueError:
        return None, "Please enter a valid number (e.g., 1500 or 99.99)."


def validate_date(date_str: str) -> tuple[str | None, str | None]:
    """
    Validate a date string in YYYY-MM-DD format.

    Args:
        date_str (str): Raw date input.

    Returns:
        tuple: (date_string, None) if valid, or (None, error_message) if not.
    """
    try:
        # datetime.strptime raises ValueError if format doesn't match
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")

        # Disallow future dates
        if parsed.date() > datetime.now().date():
            return None, "Date cannot be in the future."

        # Disallow dates more than 10 years ago (likely a typo)
        if parsed.year < datetime.now().year - 10:
            return None, "Date seems too far in the past. Please check the year."

        return parsed.strftime("%Y-%m-%d"), None

    except ValueError:
        return None, "Date must be in YYYY-MM-DD format (e.g., 2025-03-15)."


def validate_category(category: str) -> tuple[str | None, str | None]:
    """
    Validate that a category is in the approved list.

    Args:
        category (str): Raw category input.

    Returns:
        tuple: (category, None) if valid, or (None, error_message) if not.
    """
    if category in CATEGORIES:
        return category, None
    return None, f"'{category}' is not a valid category."


def validate_description(desc: str) -> tuple[str | None, str | None]:
    """
    Validate a description is not empty and not too long.

    Args:
        desc (str): Raw description input.

    Returns:
        tuple: (cleaned_desc, None) if valid, or (None, error_message) if not.
    """
    cleaned = desc.strip()

    if not cleaned:
        return None, "Description cannot be empty."
    if len(cleaned) > 200:
        return None, "Description is too long (max 200 characters)."

    return cleaned, None
