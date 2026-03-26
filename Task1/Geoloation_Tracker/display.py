"""
utils/display.py
-----------------
Terminal display helpers for the Geolocation Tracker.

Uses ANSI escape codes (the same technique as the expense tracker)
to produce coloured, formatted terminal output without any library.
"""


class C:
    """ANSI colour constants. RESET always re-applies the default terminal colour."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"


def c(text: str, color: str, bold: bool = False) -> str:
    """Wrap text in ANSI color codes."""
    b = C.BOLD if bold else ""
    return f"{b}{color}{text}{C.RESET}"


def banner() -> None:
    """Print the application startup banner."""
    lines = [
        "",
        c("  ╔══════════════════════════════════════════════════╗", C.CYAN),
        c("  ║  ", C.CYAN) + c("🌍  GEOLOCATION TRACKER", C.WHITE, bold=True) + c("  ", C.CYAN) + c("        Python CLI  ║", C.DIM),
        c("  ║  ", C.CYAN) + c("  IP → Location → Interactive Map", C.CYAN) + c("              ║", C.CYAN),
        c("  ╚══════════════════════════════════════════════════╝", C.CYAN),
        "",
    ]
    print("\n".join(lines))


def section(title: str) -> None:
    """Print a section heading."""
    print(f"\n{c('▶', C.CYAN, bold=True)} {c(title, C.WHITE, bold=True)}")
    print(c("  " + "─" * 50, C.DIM))


def kv(label: str, value: str, label_color: str = C.DIM, value_color: str = C.WHITE) -> None:
    """Print a key-value line, aligned."""
    print(f"  {c(f'{label:<16}', label_color)}  {c(str(value), value_color)}")


def success(msg: str) -> None:
    print(f"\n  {c('✓', C.GREEN, bold=True)}  {c(msg, C.GREEN)}")


def error(msg: str) -> None:
    print(f"\n  {c('✗', C.RED, bold=True)}  {c(msg, C.RED)}")


def warn(msg: str) -> None:
    print(f"\n  {c('⚠', C.YELLOW, bold=True)}  {c(msg, C.YELLOW)}")


def info(msg: str) -> None:
    print(f"  {c('ℹ', C.BLUE)}  {c(msg, C.DIM)}")


def print_location(loc: dict) -> None:
    """Pretty-print a full geolocation result to the terminal."""
    section("Location Result")
    kv("IP Address",  loc["ip"],          value_color=C.CYAN)
    kv("Fetched At",  loc["fetched_at"],  value_color=C.DIM)

    section("Geographic Info")
    kv("Country",   f"{loc['country']} ({loc['country_code']})", value_color=C.YELLOW)
    kv("Region",    loc["region"],   value_color=C.WHITE)
    kv("City",      loc["city"],     value_color=C.WHITE)
    kv("ZIP Code",  loc["zip_code"], value_color=C.WHITE)

    section("Coordinates")
    kv("Latitude",  str(loc["latitude"]),  value_color=C.MAGENTA)
    kv("Longitude", str(loc["longitude"]), value_color=C.MAGENTA)
    kv("Timezone",  loc["timezone"],       value_color=C.WHITE)

    section("Network Info")
    kv("ISP",       loc["isp"],       value_color=C.GREEN)
    kv("Org",       loc["org"],       value_color=C.WHITE)
    kv("AS Number", loc["as_number"], value_color=C.DIM)
    print()


def prompt(msg: str, default: str = "") -> str:
    """Prompt for user input with an optional default value."""
    suffix = f" [{c(default, C.DIM)}]" if default else ""
    try:
        val = input(f"\n  {c('▶', C.CYAN)} {msg}{suffix}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print()
        return default


def confirm(msg: str) -> bool:
    """Ask a yes/no question. Returns True for yes."""
    ans = prompt(f"{msg} (y/n)", default="y").lower()
    return ans in ("y", "yes", "")
