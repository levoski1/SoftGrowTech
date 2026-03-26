# 🌍 Geolocation Tracker

> **IP Address → Real-World Location → Interactive Map**
> A Python CLI application that fetches geolocation data for any IP address and renders it as a beautiful, interactive HTML map.

---

## 📌 Description

GeoTracker uses the free [ip-api.com](http://ip-api.com) API to translate any IPv4 address into its country, region, city, ISP, timezone, and GPS coordinates — then generates a rich, standalone interactive map using [Leaflet.js](https://leafletjs.com/). No Google Maps API key required.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Auto-detect IP | Discovers your public IP automatically |
| 🌐 IP Lookup | Look up any IP address on demand |
| 📡 Rich Geolocation | Country, region, city, ZIP, ISP, org, timezone |
| 🗺️ Interactive Map | Leaflet.js map with animated marker, popup, and accuracy circle |
| 🎨 Dark Theme UI | Styled terminal output with ANSI colours |
| 💾 Auto-Logging | Every lookup is saved to `data/lookup_log.json` |
| 📊 History Report | HTML report of all past lookups |
| 📦 Batch Mode | Look up multiple IPs from a text file |
| 🚩 Country Flags | Auto-generated flag emoji from country code |
| 🌙 No API Key | Works out of the box, no sign-up needed |

---

## ⚙️ Requirements

- Python **3.10+**
- `requests` library

```bash
pip install requests
```

---

## 🚀 Installation

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/geo-tracker.git
cd geo-tracker

# 2. Install the only required library
pip install requests

# 3. Run it!
python main.py
```

---

## ▶️ How to Run

```bash
# Auto-detect YOUR public IP and generate a map
python main.py

# Look up a specific IP address
python main.py --ip 8.8.8.8

# Batch lookup from a file (one IP per line)
python main.py --batch sample_ips.txt

# Open the lookup history report
python main.py --history

# Look up without generating a map
python main.py --no-map

# Look up without saving to history
python main.py --no-save

# Show all options
python main.py --help
```

---

## 📺 Sample Terminal Output

```
  ╔══════════════════════════════════════════════════╗
  ║  🌍  GEOLOCATION TRACKER           Python CLI  ║
  ║    IP → Location → Interactive Map              ║
  ╚══════════════════════════════════════════════════╝

🔍 Detecting your public IP address...
   Found: 197.210.84.12
🌍 Fetching geolocation data for 197.210.84.12...
   Done!

▶ Location Result
  ─────────────────────────────────────────────────
  IP Address       197.210.84.12
  Fetched At       2025-03-26 14:30:00

▶ Geographic Info
  ─────────────────────────────────────────────────
  Country          Nigeria (NG)
  Region           Lagos
  City             Lagos
  ZIP Code         100001

▶ Coordinates
  ─────────────────────────────────────────────────
  Latitude         6.4541
  Longitude        3.3947
  Timezone         Africa/Lagos

▶ Network Info
  ─────────────────────────────────────────────────
  ISP              MTN Nigeria Communication Limited
  Org              MTN Nigeria
  AS Number        AS29465 MTN Nigeria Communication Limited

▶ Generating Map
  ✓ Map saved → /path/to/maps/geo_197_210_84_12.html

▶ Saving Result
💾 Result saved to: data/lookup_log.json

▶ Opening Map
  ℹ Map opened in your default browser.
```

---

## 🗂️ Folder Structure

```
geo_tracker/
│
├── main.py                  # Entry point — CLI interface and orchestration
├── geo_fetcher.py           # Core — IP detection, API calls, data parsing
├── map_generator.py         # Generates standalone interactive HTML maps
├── sample_ips.txt           # Example IP list for batch mode
│
├── data/
│   └── lookup_log.json      # Auto-created — full lookup history (JSON)
│
├── maps/
│   └── geo_*.html           # Auto-created — one map per IP lookup
│
├── reports/
│   ├── __init__.py
│   ├── history_report.py    # Generates styled HTML history report
│   └── history.html         # Auto-created — the history report
│
├── utils/
│   ├── __init__.py
│   └── display.py           # Terminal output — colours, sections, prompts
│
├── DOCUMENTATION.md         # Full technical + learning documentation
└── README.md                # This file
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **requests** | HTTP API calls |
| **ip-api.com** | Free geolocation API (no key needed) |
| **api.ipify.org** | Public IP discovery |
| **Leaflet.js** | Interactive map (loaded from CDN) |
| **OpenStreetMap / CartoDB** | Map tile providers |
| **ANSI escape codes** | Terminal colours (no library) |
| **json** | Data persistence |
| **argparse** | CLI argument parsing |

---

## 🔮 Future Improvements

| Feature | Complexity | Notes |
|---|---|---|
| Streamlit web dashboard | Medium | `pip install streamlit folium streamlit-folium` |
| SQLite database backend | Medium | Replace JSON log with relational DB |
| Real-time IP monitoring | Advanced | Track an IP over time, alert on changes |
| Tkinter GUI | Medium | Desktop window with map thumbnail |
| Multi-IP comparison map | Medium | Plot all history IPs on one map |
| Reverse geocoding | Easy | Coordinates → street address via Nominatim |
| Rate limit handling | Easy | Automatic retry with exponential backoff |
| IPv6 support | Easy | ip-api.com already supports IPv6 |
| Export to CSV | Easy | Write lookup log as a spreadsheet |
| VPN detection | Advanced | Cross-reference with VPN IP databases |

---

## 📄 API Reference

### ip-api.com (Geolocation)
- **URL:** `http://ip-api.com/json/{ip}`
- **Rate Limit:** 45 requests/minute (free)
- **Docs:** http://ip-api.com/docs

### api.ipify.org (Public IP Discovery)
- **URL:** `https://api.ipify.org?format=json`
- **Rate Limit:** None (very generous)
- **Response:** `{"ip": "197.210.84.12"}`

---

## ⚠️ Limitations

- **VPNs & Proxies** will show the VPN server's location, not your physical location
- **Private IPs** (192.168.x.x, 127.0.0.1, 10.x.x.x) cannot be geolocated
- **Accuracy** is best at country level (~99%) and weaker at city level (~80%)
- **Free tier** of ip-api.com is HTTP only (HTTPS requires a paid plan)

---

## 📃 License

MIT License — free to use, modify, and distribute.

---

*Built as a structured Python learning project. Combines real API integration, data formatting, HTML generation, and CLI design in one practical tool.*
