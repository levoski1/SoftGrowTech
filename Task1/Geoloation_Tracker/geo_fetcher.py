"""
geo_fetcher.py
--------------
Core module for the Geolocation Tracker application.

Handles:
  1. Fetching the user's public IP address
  2. Querying the ip-api.com geolocation API
  3. Parsing and structuring the JSON response
  4. Error handling for network/API failures

WHY THIS MODULE?
  Separating API logic from display logic is a fundamental principle
  called "Separation of Concerns". This module knows HOW to get data;
  main.py and the map module know how to SHOW it.

LIBRARY USED: requests
  The `requests` library is the industry standard for making HTTP
  calls in Python. It turns what would be 20+ lines of raw socket
  code into a single readable line: requests.get(url)

FREE API USED: ip-api.com
  - No API key required for basic use (up to 45 requests/minute)
  - Returns JSON with country, city, lat/lon, ISP, timezone, and more
  - Documentation: http://ip-api.com/docs
"""

import requests          # Third-party: HTTP requests made simple
import json              # Standard library: parse JSON responses
import socket            # Standard library: low-level networking
from datetime import datetime  # Standard library: timestamps


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# Primary service to discover our own public IP address
# (your machine's local IP is 192.168.x.x — this reveals your internet-facing IP)
IP_DISCOVERY_URL = "https://api.ipify.org?format=json"

# ip-api.com endpoint — {ip} is replaced with the actual IP at runtime
# The `fields` parameter tells the API exactly which data we want
# (reduces response size and speeds up the request)
GEO_API_URL = (
    "http://ip-api.com/json/{ip}"
    "?fields=status,message,country,countryCode,region,regionName,"
    "city,zip,lat,lon,timezone,isp,org,as,query"
)

# How many seconds to wait before giving up on a network request
# Without this, a hung server could freeze the entire application forever
REQUEST_TIMEOUT = 10


# ─── IP DISCOVERY ─────────────────────────────────────────────────────────────

def get_public_ip() -> str:
    """
    Discover the machine's current public (internet-facing) IP address.

    WHY NOT USE socket.gethostbyname()?
      That returns your *local* network IP (e.g., 192.168.1.5), which
      is only meaningful inside your home router. Geolocation APIs need
      your *public* IP — the one the internet sees — which is assigned
      by your ISP. We have to ask an external server to tell us what IP
      our packets are coming from.

    Returns:
        str: Public IPv4 address, e.g., "197.210.84.12"

    Raises:
        ConnectionError: If the IP discovery service is unreachable.
        ValueError:      If the response doesn't contain a valid IP.
    """
    try:
        # requests.get() sends an HTTP GET request and returns a Response object
        # timeout= prevents infinite waiting if the server hangs
        response = requests.get(IP_DISCOVERY_URL, timeout=REQUEST_TIMEOUT)

        # raise_for_status() raises an exception if HTTP status is 4xx or 5xx
        # Without this, a 404 or 500 error would silently return bad data
        response.raise_for_status()

        # .json() parses the response body from a JSON string into a Python dict
        # ipify returns: {"ip": "197.210.84.12"}
        data = response.json()

        ip = data.get("ip", "").strip()

        if not ip:
            raise ValueError("IP discovery service returned an empty response.")

        return ip

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to IP discovery service. "
            "Please check your internet connection."
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(
            f"IP discovery service did not respond within {REQUEST_TIMEOUT} seconds."
        )
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error while fetching public IP: {e}")


# ─── GEOLOCATION LOOKUP ───────────────────────────────────────────────────────

def get_geolocation(ip: str) -> dict:
    """
    Query the ip-api.com API to get geolocation data for a given IP address.

    HOW IP GEOLOCATION WORKS (simplified):
      1. Every IP address is "registered" with an organisation (ISP, company, etc.)
      2. These registrations are recorded in public WHOIS/ARIN databases
      3. ISPs are physically located in specific countries and cities
      4. ip-api.com maintains a database that maps IP ranges → physical locations
         by cross-referencing these registrations with observed routing patterns
      5. Accuracy: country (~99%), region (~90%), city (~80%), lat/lon varies

    Args:
        ip (str): Any valid IPv4 or IPv6 address.

    Returns:
        dict: Structured geolocation data with keys:
              ip, country, country_code, region, city, zip_code,
              latitude, longitude, timezone, isp, org, as_number,
              fetched_at (timestamp)

    Raises:
        ConnectionError: If the API is unreachable.
        ValueError:      If the API returns a "fail" status.
    """
    # Build the URL by substituting the real IP into our template
    url = GEO_API_URL.format(ip=ip)

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        raw = response.json()

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to geolocation API (ip-api.com). "
            "Check your internet connection."
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(
            f"Geolocation API timed out after {REQUEST_TIMEOUT} seconds."
        )
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during geolocation lookup: {e}")
    except json.JSONDecodeError:
        raise ValueError("Geolocation API returned invalid JSON.")

    # ip-api.com signals success/failure with a "status" field
    # Possible values: "success" or "fail"
    if raw.get("status") != "success":
        error_msg = raw.get("message", "Unknown API error")
        raise ValueError(
            f"Geolocation API returned an error for IP '{ip}': {error_msg}\n"
            "This can happen for private/reserved IPs (e.g., 127.0.0.1, 192.168.x.x)."
        )

    # Transform the raw API response into our own clean dictionary structure.
    # WHY REMAP KEYS?
    #   The API uses abbreviated keys like "countryCode" and "regionName".
    #   Our internal structure uses clearer names and groups related data.
    #   This also insulates the rest of the app from API changes — if ip-api.com
    #   ever renames a field, we only fix it here.
    location = {
        # ── Identity ──────────────────────────────────────────────
        "ip":           raw.get("query", ip),
        "fetched_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # ── Location hierarchy ────────────────────────────────────
        "country":      raw.get("country", "Unknown"),
        "country_code": raw.get("countryCode", "??"),
        "region":       raw.get("regionName", "Unknown"),
        "region_code":  raw.get("region", "??"),
        "city":         raw.get("city", "Unknown"),
        "zip_code":     raw.get("zip", "N/A"),

        # ── Coordinates (the KEY values for map plotting) ─────────
        "latitude":     float(raw.get("lat", 0.0)),
        "longitude":    float(raw.get("lon", 0.0)),

        # ── Time ──────────────────────────────────────────────────
        "timezone":     raw.get("timezone", "Unknown"),

        # ── Network identity ─────────────────────────────────────
        "isp":          raw.get("isp", "Unknown"),
        "org":          raw.get("org", "Unknown"),
        "as_number":    raw.get("as", "Unknown"),
    }

    return location


# ─── CONVENIENCE WRAPPER ──────────────────────────────────────────────────────

def lookup(ip: str = None) -> dict:
    """
    High-level convenience function: auto-detect IP if not provided,
    then fetch and return full geolocation data.

    This is the main function most callers will use — they don't need
    to call get_public_ip() and get_geolocation() separately.

    Args:
        ip (str | None): IP to look up. If None, auto-detects current public IP.

    Returns:
        dict: Full geolocation result.
    """
    if ip is None:
        print("🔍 Detecting your public IP address...")
        ip = get_public_ip()
        print(f"   Found: {ip}")

    print(f"🌍 Fetching geolocation data for {ip}...")
    location = get_geolocation(ip)
    print("   Done!\n")

    return location


# ─── FORMATTING HELPERS ───────────────────────────────────────────────────────

def format_location_summary(loc: dict) -> str:
    """
    Format a geolocation result into a human-readable multi-line string
    suitable for terminal display.

    Args:
        loc (dict): Result from lookup() or get_geolocation().

    Returns:
        str: Pretty-printed location summary.
    """
    # Flag emoji from country code: each letter maps to a regional indicator symbol
    # e.g., "NG" → 🇳🇬, "US" → 🇺🇸
    def country_flag(code: str) -> str:
        if not code or len(code) != 2:
            return "🌐"
        # Unicode regional indicator symbols start at U+1F1E6 (= ord('A') + offset)
        offset = ord("🇦") - ord("A")
        return "".join(chr(ord(c) + offset) for c in code.upper())

    flag = country_flag(loc.get("country_code", ""))

    lines = [
        "─" * 52,
        f"  IP Address   : {loc['ip']}",
        f"  Looked up    : {loc['fetched_at']}",
        "─" * 52,
        f"  {flag}  Country   : {loc['country']} ({loc['country_code']})",
        f"  📍  Region    : {loc['region']} ({loc['region_code']})",
        f"  🏙️  City       : {loc['city']}",
        f"  📮  ZIP Code   : {loc['zip_code']}",
        "─" * 52,
        f"  🌐  Latitude   : {loc['latitude']}",
        f"  🌐  Longitude  : {loc['longitude']}",
        f"  🕐  Timezone   : {loc['timezone']}",
        "─" * 52,
        f"  📡  ISP        : {loc['isp']}",
        f"  🏢  Org        : {loc['org']}",
        f"  🔢  AS Number  : {loc['as_number']}",
        "─" * 52,
    ]

    return "\n".join(lines)


# ─── DATA PERSISTENCE ─────────────────────────────────────────────────────────

def save_result(location: dict, filepath: str = "data/lookup_log.json") -> None:
    """
    Append a geolocation result to a JSON log file.

    WHY APPEND INSTEAD OF OVERWRITE?
      Keeping a history of all lookups is more useful than a single result.
      A user tracking multiple IPs or running the app daily gets a full audit trail.

    Args:
        location (dict): The geolocation result to save.
        filepath (str):  Path to the JSON log file.
    """
    import os

    # Ensure the target directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Load existing records (or start fresh if file doesn't exist)
    existing = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []   # Reset if file was corrupted
        except (json.JSONDecodeError, IOError):
            existing = []

    # Append the new record
    existing.append(location)

    # Write the updated list back to the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print(f"💾 Result saved to: {filepath}")
