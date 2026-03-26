"""
utils/display.py
-----------------
All display/formatting helpers for the terminal UI.

WHY SEPARATE DISPLAY HELPERS?
  Formatting logic (colors, tables, menus) has nothing to do with
  business logic. Keeping it here means main.py stays clean,
  and if you later switch to a web UI, you only change this file.
"""

from datetime import datetime


# ─── ANSI COLOR CODES ─────────────────────────────────────────────────────────
# These are special escape sequences that most terminals understand.
# They let us print colored text without any extra library.

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"


def colored(text: str, color: str) -> str:
    """Wrap text with an ANSI color code and reset."""
    return f"{color}{text}{Color.RESET}"


def bold(text: str) -> str:
    return f"{Color.BOLD}{text}{Color.RESET}"


# ─── LAYOUT HELPERS ───────────────────────────────────────────────────────────

def divider(char: str = "─", width: int = 60) -> str:
    """Return a horizontal divider line."""
    return colored(char * width, Color.DIM)


def header(title: str, width: int = 60) -> str:
    """Return a formatted section header."""
    line = "═" * width
    padded = title.center(width)
    return (
        f"\n{colored(line, Color.CYAN)}\n"
        f"{colored(padded, Color.BOLD)}\n"
        f"{colored(line, Color.CYAN)}"
    )


def print_menu(title: str, options: list[str]) -> None:
    """
    Print a numbered menu with a title.

    Args:
        title   (str):        The menu heading.
        options (list[str]):  Menu options (will be numbered 1..N).
    """
    print(header(title))
    for i, option in enumerate(options, start=1):
        # Right-align the number, then print the option
        print(f"  {colored(str(i), Color.CYAN)}.  {option}")
    print(divider())


# ─── EXPENSE DISPLAY ──────────────────────────────────────────────────────────

def format_amount(amount: float, currency: str = "₦") -> str:
    """
    Format a number as a currency string.

    Args:
        amount   (float): The amount to format.
        currency (str):   Currency symbol prefix.

    Returns:
        str: e.g., "₦1,250.00"
    """
    # f-string ":,.2f" formats with commas and 2 decimal places
    return f"{currency}{amount:,.2f}"


def format_expense_row(expense: dict, index: int = None) -> str:
    """
    Format a single expense as a readable terminal row.

    Args:
        expense (dict): The expense record.
        index   (int):  Optional row number to display.

    Returns:
        str: A formatted string for display.
    """
    # Choose color based on amount size
    amount = expense["amount"]
    if amount >= 10_000:
        amount_color = Color.RED
    elif amount >= 5_000:
        amount_color = Color.YELLOW
    else:
        amount_color = Color.GREEN

    idx_str = f"{colored(str(index) + '.', Color.DIM):<6}" if index is not None else ""

    return (
        f"{idx_str}"
        f"{colored(expense['id'], Color.DIM):<10}  "
        f"{colored(expense['date'], Color.BLUE):<12}  "
        f"{colored(format_amount(amount), amount_color):<14}  "
        f"{colored(expense['category'], Color.MAGENTA):<22}  "
        f"{expense['description']}"
    )


def print_expense_table(expenses: list[dict], title: str = "Expenses") -> None:
    """
    Print a formatted table of expenses.

    Args:
        expenses (list[dict]): The expenses to display.
        title    (str):        Table heading.
    """
    print(header(title))

    if not expenses:
        print(colored("  No expenses found.", Color.YELLOW))
        print(divider())
        return

    # Column headers
    print(
        f"{'':6}"
        f"{'ID':<10}  "
        f"{'Date':<12}  "
        f"{'Amount':>14}  "
        f"{'Category':<22}  "
        f"{'Description'}"
    )
    print(divider())

    for i, expense in enumerate(expenses, start=1):
        print(format_expense_row(expense, index=i))

    print(divider())
    total = sum(e["amount"] for e in expenses)
    print(f"  {bold('Total:'):>52}  {colored(format_amount(total), Color.GREEN)}")
    print(divider())


def print_category_chart(breakdown: list[dict]) -> None:
    """
    Print a text-based bar chart of spending by category.

    This gives a visual representation without needing matplotlib.

    Args:
        breakdown (list[dict]): Output from analytics.get_category_breakdown().
    """
    print(header("Spending by Category"))

    if not breakdown:
        print(colored("  No data available.", Color.YELLOW))
        return

    max_bar = 30   # Maximum bar width in characters

    for item in breakdown:
        # Scale bar length relative to the highest-spending category
        bar_len = int((item["percentage"] / 100) * max_bar)
        bar = "█" * bar_len

        print(
            f"  {item['category']:<22}  "
            f"{colored(bar, Color.CYAN):<{max_bar + 10}}  "
            f"{colored(format_amount(item['total']), Color.GREEN):<12}  "
            f"{colored(str(item['percentage']) + '%', Color.YELLOW)}"
        )

    print(divider())


def print_monthly_chart(monthly: list[dict]) -> None:
    """
    Print a text-based bar chart of monthly spending.

    Args:
        monthly (list[dict]): Output from analytics.get_monthly_summary().
    """
    print(header("Monthly Spending Overview"))

    if not monthly:
        print(colored("  No data available.", Color.YELLOW))
        return

    max_amount = max(m["total"] for m in monthly)
    max_bar = 35

    for item in monthly:
        bar_len = int((item["total"] / max_amount) * max_bar) if max_amount else 0
        bar = "▓" * bar_len

        # Convert "2025-03" → "Mar 2025" for readability
        try:
            label = datetime.strptime(item["month"], "%Y-%m").strftime("%b %Y")
        except ValueError:
            label = item["month"]

        print(
            f"  {label:<12}  "
            f"{colored(bar, Color.BLUE):<{max_bar + 10}}  "
            f"{colored(format_amount(item['total']), Color.GREEN)}"
        )

    print(divider())


# ─── INPUT HELPERS ────────────────────────────────────────────────────────────

def prompt(message: str, default: str = "") -> str:
    """
    Display a prompt and return the user's input.
    If the user presses Enter without typing, return the default.

    Args:
        message (str): Prompt text to display.
        default (str): Fallback value if input is empty.

    Returns:
        str: The user's input, or the default.
    """
    suffix = f" [{default}]" if default else ""
    user_input = input(f"{colored('▶', Color.CYAN)} {message}{suffix}: ").strip()
    return user_input if user_input else default


def prompt_float(message: str, min_val: float = 0.01) -> float:
    """
    Prompt for a float value, retrying until valid input is given.

    Args:
        message (str):   Prompt text.
        min_val (float): Minimum acceptable value.

    Returns:
        float: A valid float above min_val.
    """
    while True:
        raw = prompt(message)
        try:
            value = float(raw)
            if value < min_val:
                print(colored(f"  ✗ Amount must be at least {min_val}.", Color.RED))
            else:
                return value
        except ValueError:
            print(colored("  ✗ Please enter a valid number (e.g., 1500 or 99.99).", Color.RED))


def prompt_choice(options: list[str], message: str = "Choose an option") -> int:
    """
    Prompt the user to choose from a numbered list.

    Args:
        options (list[str]): The choices to display.
        message (str):       Prompt label.

    Returns:
        int: Zero-based index of the selected option.
    """
    print_menu("", options)
    while True:
        raw = prompt(message)
        try:
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice - 1   # Convert to zero-based index
            print(colored(f"  ✗ Please enter a number between 1 and {len(options)}.", Color.RED))
        except ValueError:
            print(colored("  ✗ Please enter a number.", Color.RED))


def confirm(message: str) -> bool:
    """
    Ask a yes/no confirmation question.

    Args:
        message (str): The question to ask.

    Returns:
        bool: True for yes, False for no.
    """
    answer = prompt(f"{message} (y/n)").lower()
    return answer in ("y", "yes")


def success(message: str) -> None:
    """Print a green success message."""
    print(colored(f"\n  ✓ {message}", Color.GREEN))


def error(message: str) -> None:
    """Print a red error message."""
    print(colored(f"\n  ✗ {message}", Color.RED))


def info(message: str) -> None:
    """Print a blue informational message."""
    print(colored(f"\n  ℹ {message}", Color.BLUE))
