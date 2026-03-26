# 📚 Geolocation Tracker — Complete Project Documentation

> **Audience:** Python beginners transitioning to intermediate level
> **Goal:** Understand how IP geolocation works and how to build production-quality tools around it

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [How IP Geolocation Works](#2-how-ip-geolocation-works)
3. [Real-World Use Cases](#3-real-world-use-cases)
4. [Step-by-Step Task Roadmap](#4-step-by-step-task-roadmap)
5. [Task 1 — Detect Public IP](#task-1--detect-public-ip)
6. [Task 2 — Fetch Geolocation from API](#task-2--fetch-geolocation-from-api)
7. [Task 3 — Parse & Structure the Response](#task-3--parse--structure-the-response)
8. [Task 4 — Terminal Display](#task-4--terminal-display)
9. [Task 5 — Interactive HTML Map](#task-5--interactive-html-map)
10. [Task 6 — Data Persistence & Logging](#task-6--data-persistence--logging)
11. [Task 7 — CLI Arguments & Batch Mode](#task-7--cli-arguments--batch-mode)
12. [Task 8 — History Report](#task-8--history-report)
13. [Libraries & Tools Explained](#libraries--tools-explained)
14. [Best Practices Applied](#best-practices-applied)
15. [Error Handling Strategy](#error-handling-strategy)
16. [Key Python Concepts](#key-python-concepts)
17. [Optional Advanced Features](#optional-advanced-features)

---

## 1. Project Overview

The **Geolocation Tracker** is a command-line Python application that:

1. Detects (or accepts) an IP address
2. Queries a free geolocation API to discover where that IP is physically located
3. Displays detailed location data in the terminal
4. Generates a fully interactive HTML map centred on the coordinates
5. Logs all lookups to a JSON file for history tracking
6. Generates a styled HTML history report

It requires only the `requests` library (for HTTP calls). The map is generated using **Leaflet.js** loaded from a CDN, embedded into a self-contained HTML file.

---

## 2. How IP Geolocation Works

Understanding the mechanism makes you a better developer. Here is what happens, step by step:

### Step 1: Every device has two IPs

| Type | Example | Who Sees It |
|------|---------|-------------|
| Private/Local IP | `192.168.1.5` | Only your home network |
| Public IP | `197.210.84.12` | The entire internet |

When you send a request to Google, your router substitutes your private IP with your public IP (a process called **NAT — Network Address Translation**).

### Step 2: IP addresses are registered

Every IP address is assigned to an organisation (an ISP, company, university, etc.) through a system of **Regional Internet Registries (RIRs)**:

| Registry | Region |
|----------|--------|
| ARIN | North America |
| RIPE NCC | Europe, Middle East |
| AFRINIC | Africa |
| APNIC | Asia-Pacific |
| LACNIC | Latin America |

These registrations are public. You can look up any IP at [whois.arin.net](https://whois.arin.net).

### Step 3: ISPs are physically located

An ISP based in Lagos, Nigeria owns a block of IP addresses. When your device gets one of those IPs, there's a strong probability that you're physically near Lagos.

### Step 4: Cross-referencing builds the database

Companies like ip-api.com maintain databases that cross-reference:
- WHOIS registration data
- BGP routing tables (which routers handle which IPs)
- Observed network latency patterns
- Crowdsourced location signals

### Step 5: Accuracy varies by level

| Level | Typical Accuracy |
|-------|-----------------|
| Country | ~99% |
| Region/State | ~90% |
| City | ~80% |
| Street Address | ❌ Not reliable |
| Exact lat/lon | Varies widely |

**Important:** VPNs and proxies deliberately break this chain by routing traffic through servers in different locations.

---

## 3. Real-World Use Cases

| Use Case | How It Works |
|----------|-------------|
| **Content Localisation** | Netflix shows different titles based on detected country |
| **Fraud Detection** | Banks flag logins from unexpected countries |
| **Security Analytics** | Server logs show where attacks originate |
| **Ad Targeting** | Show ads relevant to the user's region |
| **Access Control** | Restrict services to specific countries |
| **Weather/News Apps** | Auto-populate local weather without asking the user |
| **CDN Routing** | Serve assets from the nearest data centre |
| **Analytics Dashboards** | Visualise where your users are coming from |

---

## 4. Step-by-Step Task Roadmap

| Day | Task | Skill Learned |
|-----|------|--------------|
| Day 1 | Detect public IP | `requests`, API calls |
| Day 2 | Fetch geolocation | JSON parsing, API responses |
| Day 3 | Parse & structure data | Dict manipulation, data modelling |
| Day 4 | Terminal display | ANSI colours, f-strings, formatting |
| Day 5 | Interactive map | HTML generation, Leaflet.js |
| Day 6 | Data persistence | File I/O, JSON, logging |
| Day 7 | CLI arguments | `argparse`, modular design |
| Day 8 | History report | Template generation, data aggregation |

---

## Task 1 — Detect Public IP

### Objective
Discover the machine's internet-facing IP address, which is what geolocation APIs use.

### Why Can't We Use `socket`?
```python
import socket
local_ip = socket.gethostbyname(socket.gethostname())
# Returns: "192.168.1.5" — your HOME network IP, useless for geolocation
```

We need to ask an *external* server what IP they see our request coming from:

```python
import requests

response = requests.get("https://api.ipify.org?format=json", timeout=10)
data = response.json()        # {"ip": "197.210.84.12"}
public_ip = data["ip"]
```

### Key Concepts
- `requests.get(url, timeout=10)` — makes an HTTP GET request, gives up after 10 seconds
- `.raise_for_status()` — raises an exception if the server returned an error (4xx, 5xx)
- `.json()` — parses the JSON response body into a Python dictionary

---

## Task 2 — Fetch Geolocation from API

### Objective
Use ip-api.com to translate an IP address into location data.

### The API
```
http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,...
```

- **Free** for non-commercial use (45 req/min)
- **No API key required**
- Returns JSON with 20+ data points

### Example Request & Response

```python
import requests

ip = "197.210.84.12"
url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,lat,lon,isp,timezone"

response = requests.get(url, timeout=10)
data = response.json()
```

```json
{
  "status": "success",
  "country": "Nigeria",
  "countryCode": "NG",
  "city": "Lagos",
  "lat": 6.4541,
  "lon": 3.3947,
  "isp": "MTN Nigeria Communication Limited",
  "timezone": "Africa/Lagos"
}
```

### Error Handling
The API signals errors with `"status": "fail"` (not HTTP errors):
```python
if data.get("status") != "success":
    error_msg = data.get("message", "Unknown error")
    raise ValueError(f"API error: {error_msg}")
```

This is important — the API returns **HTTP 200** even for failures, so you can't rely on `raise_for_status()` alone.

---

## Task 3 — Parse & Structure the Response

### Objective
Transform the raw API response into a clean, consistent internal format.

### Why Remap Keys?
The API returns `"countryCode"`, `"regionName"`, `"lat"`, `"lon"`. Our app uses `"country_code"`, `"region"`, `"latitude"`, `"longitude"`. This remapping:

1. Uses more readable names throughout the codebase
2. Insulates the app from API changes (if ip-api.com renames `"lat"` to `"latitude"`, we only fix it in one place)
3. Ensures consistent types (we always cast lat/lon to `float`)

```python
location = {
    "ip":           raw.get("query", ip),
    "country":      raw.get("country", "Unknown"),
    "country_code": raw.get("countryCode", "??"),
    "latitude":     float(raw.get("lat", 0.0)),    # Always float
    "longitude":    float(raw.get("lon", 0.0)),    # Always float
    # ... etc
}
```

### `.get()` with defaults
`dict.get("key", "default")` is safer than `dict["key"]` because it never raises `KeyError` — it returns the default instead. Always use `.get()` with API responses, because external APIs can change their schema.

---

## Task 4 — Terminal Display

### Objective
Present the data clearly in the terminal using colour and formatting.

### ANSI Colour Codes (No Library Needed)
```python
class C:
    CYAN  = "\033[96m"
    GREEN = "\033[92m"
    RESET = "\033[0m"    # Returns to default

print(f"\033[96mLagos\033[0m")   # Prints "Lagos" in cyan
```

These escape sequences are interpreted by the terminal, not Python. They work in every Unix terminal and in Windows Terminal on Windows 10+.

### Flag Emoji from Country Code
```python
def country_flag(code: str) -> str:
    offset = ord("🇦") - ord("A")
    return "".join(chr(ord(c) + offset) for c in code.upper())

# country_flag("NG") → "🇳🇬"
# country_flag("US") → "🇺🇸"
```

Unicode's regional indicator symbols (U+1F1E6–U+1F1FF) map exactly to A–Z. Pairing two of them produces a flag emoji. This is a clever trick that requires no emoji database.

---

## Task 5 — Interactive HTML Map

### Objective
Generate a standalone HTML file with an interactive map using Leaflet.js.

### Why Leaflet.js Instead of Folium?
| Aspect | Folium (Python) | Leaflet.js (JavaScript) |
|--------|----------------|------------------------|
| Installation | `pip install folium` | No install — CDN |
| Customisation | Limited | Complete |
| Performance | Good | Excellent |
| Map themes | Few | Hundreds |
| File size | Larger | Smaller |

By writing the Leaflet.js code directly in Python strings, we get full control with zero dependencies.

### Key Leaflet Concepts

```javascript
// 1. Create map centred on coordinates, zoom level 13
const map = L.map('map', { center: [6.4541, 3.3947], zoom: 13 });

// 2. Add a tile layer (the actual map images)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// 3. Place a marker at the coordinates
L.marker([6.4541, 3.3947]).addTo(map).bindPopup('Lagos, Nigeria');

// 4. Draw a circle to show location uncertainty
L.circle([6.4541, 3.3947], { radius: 5000 }).addTo(map);
```

### Tile Layers Explained
A "tile" is a 256×256 pixel image. The map is made of hundreds of these tiles, fetched based on zoom level and viewport position. Different providers offer different visual styles:
- **OpenStreetMap** — free, detailed street map
- **CartoDB Dark** — dark theme, good for dashboards
- **Mapbox** — commercial, high-quality (requires API key)

---

## Task 6 — Data Persistence & Logging

### Objective
Save every lookup to a JSON file so the user has a searchable history.

### Append-Only Log Pattern
```python
def save_result(location: dict, filepath: str = "data/lookup_log.json") -> None:
    existing = []
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing = json.load(f)

    existing.append(location)       # Add new record

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=4)
```

We load all records, append the new one, and write everything back. This is fine for small datasets. For larger datasets, you'd use a database with proper `INSERT` operations.

---

## Task 7 — CLI Arguments & Batch Mode

### Objective
Make the app flexible — usable from the command line with flags.

### `argparse` — The Standard CLI Library

```python
import argparse

parser = argparse.ArgumentParser(description="Geolocation Tracker")
parser.add_argument("--ip",      help="IP address to look up")
parser.add_argument("--batch",   help="File with multiple IPs")
parser.add_argument("--history", action="store_true", help="Show history")
parser.add_argument("--no-map",  action="store_true", help="Skip map")

args = parser.parse_args()
```

After calling `parse_args()`, you access values as `args.ip`, `args.batch`, etc. `argparse` automatically handles:
- `--help` text generation
- Type validation
- Mutually exclusive groups

### Batch Mode Pattern
```python
with open(filepath) as f:
    ips = [line.strip() for line in f
           if line.strip() and not line.strip().startswith("#")]

for ip in ips:
    location = lookup(ip)
    save_result(location)
    generate_map(location, f"maps/geo_{ip}.html")
```

---

## Task 8 — History Report

### Objective
Generate a styled HTML page showing all past lookups.

### HTML Generation from Python
We build the HTML string using f-strings and Python list comprehensions:

```python
rows = "\n".join(
    f"<tr><td>{r['ip']}</td><td>{r['country']}</td></tr>"
    for r in records
)
html = f"<table>{rows}</table>"
```

This is the foundation of every web framework's template engine. Django's templates, Jinja2, and Flask's `render_template` all do essentially this, just with more features.

---

## Libraries & Tools Explained

| Library/Tool | Type | Why Used |
|---|---|---|
| `requests` | 3rd-party | Industry-standard HTTP client; cleaner than `urllib` |
| `json` | stdlib | Parse API responses and read/write the data log |
| `os` | stdlib | File path operations, directory creation |
| `argparse` | stdlib | Professional CLI argument parsing |
| `webbrowser` | stdlib | Open generated files in the user's browser |
| `datetime` | stdlib | Timestamps for log entries |
| `uuid` | stdlib | Not used here, but relevant for unique record IDs |
| Leaflet.js | CDN JS | The world's leading open-source mapping library |
| ip-api.com | Free API | Geolocation data, no API key, 45 req/min free |
| api.ipify.org | Free API | Returns your public IP as JSON |

---

## Best Practices Applied

### 1. Separation of Concerns
Each file has one responsibility:
- `geo_fetcher.py` → API calls only
- `map_generator.py` → HTML/map generation only
- `utils/display.py` → Terminal output only
- `main.py` → User flow and orchestration only

### 2. Never Trust External APIs
All API calls are wrapped in `try/except` with specific error types:
```python
except requests.exceptions.ConnectionError: # No internet
except requests.exceptions.Timeout:         # Server too slow
except requests.exceptions.RequestException: # Any other HTTP error
except json.JSONDecodeError:                 # Malformed response
```

### 3. Validate API Status Fields
Many APIs return HTTP 200 even for errors. Always check their status field:
```python
if raw.get("status") != "success":
    raise ValueError(raw.get("message", "Unknown error"))
```

### 4. Safe Dictionary Access
```python
# ❌ Dangerous — raises KeyError if key missing
country = raw["country"]

# ✅ Safe — returns "Unknown" if key missing
country = raw.get("country", "Unknown")
```

### 5. Type Coercion at the Boundary
Convert types immediately when receiving external data:
```python
"latitude": float(raw.get("lat", 0.0))   # Always a float, never a string
```

---

## Error Handling Strategy

The app uses a layered approach:

```
User Input
    │
    ▼
main.py ─── try/except ──→ display error() and sys.exit(1)
    │
    ▼
geo_fetcher.py ─── raises ConnectionError / ValueError
    │
    ▼
requests library ─── raises RequestException subtypes
    │
    ▼
HTTP/Network layer
```

Each layer handles what it knows about. `requests` handles HTTP; `geo_fetcher` translates to domain errors; `main.py` handles user-facing messages.

---

## Key Python Concepts

| Concept | Where Used | Why It Matters |
|---|---|---|
| `f-strings` | Everywhere | Clean string formatting |
| `dict.get(key, default)` | API parsing | Safe key access |
| `try/except` with specific types | geo_fetcher.py | Precise error handling |
| `argparse` | main.py | Professional CLI interface |
| `os.makedirs(exist_ok=True)` | All file writers | Safe directory creation |
| `json.load/dump` | Data persistence | Python ↔ JSON |
| List comprehensions | Batch mode, HTML generation | Concise list building |
| `webbrowser.open()` | main.py | Platform-agnostic browser launch |
| `sys.exit(1)` | Error paths | Signal failure to shell |
| f-string `:.4f` | Coordinates | 4 decimal places formatting |

---

## Optional Advanced Features

### 1. Streamlit Web Dashboard
```bash
pip install streamlit folium streamlit-folium
```
```python
import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🌍 Geolocation Tracker")
ip = st.text_input("Enter IP address")
if ip:
    location = lookup(ip)
    m = folium.Map(location=[location["latitude"], location["longitude"]])
    folium.Marker([location["latitude"], location["longitude"]]).add_to(m)
    st_folium(m, width=700)
```

### 2. SQLite Database Backend
```python
import sqlite3

conn = sqlite3.connect("data/geotracker.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS lookups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT, country TEXT, city TEXT,
        latitude REAL, longitude REAL,
        isp TEXT, fetched_at TEXT
    )
""")
conn.execute(
    "INSERT INTO lookups VALUES (?,?,?,?,?,?,?,?)",
    (loc["ip"], loc["country"], loc["city"],
     loc["latitude"], loc["longitude"],
     loc["isp"], loc["fetched_at"])
)
conn.commit()
```

### 3. Real-Time Dashboard (FastAPI + WebSockets)
```python
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        location = lookup()
        await ws.send_json(location)
        await asyncio.sleep(60)  # Re-check every minute
```

### 4. Tkinter GUI
```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("GeoTracker")
ip_var = tk.StringVar()

tk.Entry(root, textvariable=ip_var).pack()
tk.Button(root, text="Look Up", command=lambda: run_lookup(ip_var.get())).pack()
```

### 5. Multiple IP Comparison Map
Generate a single map with markers for ALL IPs in the history, connected by lines to show routing paths or attack patterns.

### 6. Reverse Geocoding
Convert raw coordinates into a street address using the Nominatim API (OpenStreetMap's geocoding service — free):
```python
url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
response = requests.get(url, headers={"User-Agent": "GeoTracker/1.0"})
address = response.json().get("display_name")
```
