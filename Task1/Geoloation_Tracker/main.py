"""
main.py
--------
Entry point for the Geolocation Tracker application.

Run this file to start the application:
  python main.py                    ← auto-detect your IP
  python main.py --ip 8.8.8.8      ← look up a specific IP
  python main.py --batch ips.txt   ← look up multiple IPs from a file
  python main.py --history          ← show past lookups report

ARCHITECTURE (Model-View-Controller):
  geo_fetcher.py      → Model      (data fetching and persistence)
  map_generator.py    → View/Map   (HTML map output)
  utils/display.py    → View/CLI   (terminal output)
  reports/            → View/HTML  (history report)
  main.py             → Controller (ties it all together)
"""

import sys
import os
import argparse    # Standard library: parse command-line arguments

# Add project root to Python path so our local imports work correctly
sys.path.insert(0, os.path.dirname(__file__))

from geo_fetcher import lookup, save_result, format_location_summary
from map_generator import generate_map
from display import (
    banner, section, print_location, success, error, warn, info, confirm, c, C
)
from history_report import generate_history_report


# ─── SINGLE IP LOOKUP ─────────────────────────────────────────────────────────

def run_lookup(ip: str = None, open_map: bool = True, save: bool = True) -> dict:
    """
    Run a full geolocation lookup: fetch → display → map → save.

    Args:
        ip       (str | None): IP to look up. None = auto-detect.
        open_map (bool):       Whether to open the HTML map in a browser.
        save     (bool):       Whether to save the result to the log.

    Returns:
        dict: The geolocation result.
    """
    # ── Fetch ──────────────────────────────────────────────────────────────
    try:
        location = lookup(ip)
    except (ConnectionError, ValueError) as e:
        error(str(e))
        sys.exit(1)

    # ── Display in terminal ────────────────────────────────────────────────
    print_location(location)

    # ── Generate interactive map ───────────────────────────────────────────
    section("Generating Map")
    ip_slug = location["ip"].replace(".", "_")
    map_path = f"maps/geo_{ip_slug}.html"

    try:
        abs_map_path = generate_map(location, output_path=map_path)
        success(f"Map saved → {abs_map_path}")
    except Exception as e:
        error(f"Map generation failed: {e}")
        abs_map_path = None

    # ── Save to log ────────────────────────────────────────────────────────
    if save:
        section("Saving Result")
        try:
            save_result(location)
        except Exception as e:
            warn(f"Could not save result: {e}")

    # ── Open map in browser ────────────────────────────────────────────────
    if abs_map_path and open_map:
        section("Opening Map")
        try:
            import webbrowser
            # webbrowser.open() launches the system's default browser
            # 'file://' prefix is required to open a local HTML file
            webbrowser.open(f"file://{abs_map_path}")
            info("Map opened in your default browser.")
        except Exception as e:
            info(f"Could not auto-open browser. Open manually: {abs_map_path}")

    return location


# ─── BATCH LOOKUP ─────────────────────────────────────────────────────────────

def run_batch(filepath: str) -> None:
    """
    Look up multiple IP addresses from a plain-text file (one IP per line).

    WHY BATCH?
      In security and analytics, you often need to check dozens of IPs at once
      — e.g., from server logs, a list of suspicious addresses, etc.

    Args:
        filepath (str): Path to a text file with one IP per line.
    """
    if not os.path.exists(filepath):
        error(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        # Strip whitespace, skip blank lines and comment lines (# prefix)
        ips = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    if not ips:
        warn("The file contains no valid IP addresses.")
        return

    section(f"Batch Lookup — {len(ips)} IP(s)")
    results = []

    for i, ip in enumerate(ips, start=1):
        print(f"\n  [{i}/{len(ips)}] Looking up {c(ip, C.CYAN)}...")
        try:
            # open_map=False for batch — we'll generate one summary map instead
            location = lookup(ip)
            print_location(location)
            save_result(location)
            results.append(location)

            # Generate individual map for each IP
            ip_slug = ip.replace(".", "_")
            map_path = generate_map(location, output_path=f"maps/geo_{ip_slug}.html")
            info(f"Map saved: {map_path}")

        except (ConnectionError, ValueError) as e:
            error(f"Failed for {ip}: {e}")

    # Generate combined history report
    report_path = generate_history_report()
    success(f"\nBatch complete! {len(results)}/{len(ips)} succeeded.")
    success(f"History report → {report_path}")

    try:
        import webbrowser
        webbrowser.open(f"file://{report_path}")
    except Exception:
        pass


# ─── HISTORY REPORT ───────────────────────────────────────────────────────────

def run_history() -> None:
    """Generate and open the lookup history HTML report."""
    section("Lookup History Report")
    report_path = generate_history_report()
    success(f"Report generated → {report_path}")

    try:
        import webbrowser
        webbrowser.open(f"file://{report_path}")
        info("Report opened in your default browser.")
    except Exception:
        info(f"Open manually: {report_path}")


# ─── CLI ARGUMENT PARSER ──────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """
    Set up and parse command-line arguments.

    argparse is Python's built-in CLI argument parsing library.
    It automatically generates --help text and validates inputs.
    """
    parser = argparse.ArgumentParser(
        prog="geotracker",
        description="🌍 Geolocation Tracker — IP address → interactive map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Auto-detect your IP
  python main.py --ip 8.8.8.8        # Look up Google's DNS server
  python main.py --ip 1.1.1.1        # Look up Cloudflare's DNS server
  python main.py --batch ips.txt     # Batch lookup from a file
  python main.py --history           # Show lookup history report
  python main.py --no-map            # Lookup only, skip map generation
  python main.py --no-save           # Lookup only, don't log the result
        """,
    )

    # Mutually exclusive group: user picks ONE mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--ip",
        metavar="ADDRESS",
        help="IP address to look up (default: auto-detect your own IP)",
    )
    mode.add_argument(
        "--batch",
        metavar="FILE",
        help="Text file with one IP address per line for bulk lookup",
    )
    mode.add_argument(
        "--history",
        action="store_true",
        help="Generate and open the HTML lookup history report",
    )

    # Optional flags
    parser.add_argument(
        "--no-map",
        action="store_true",
        help="Skip map generation (terminal output only)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save this lookup to the history log",
    )

    return parser.parse_args()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Application entry point."""
    banner()

    args = parse_args()

    if args.history:
        run_history()

    elif args.batch:
        run_batch(args.batch)

    else:
        # Single IP lookup (or auto-detect)
        run_lookup(
            ip=args.ip,                          # None = auto-detect
            open_map=not args.no_map,
            save=not args.no_save,
        )


# Standard Python entry-point guard
if __name__ == "__main__":
    main()
