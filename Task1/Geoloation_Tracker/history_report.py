"""
reports/history_report.py
--------------------------
Generates a beautiful HTML history report from the lookup log.

Opens in a browser and shows all past IP lookups in a styled table
with colour-coded entries and summary stats.
"""

import json
import os
from datetime import datetime


def generate_history_report(log_path: str = "data/lookup_log.json",
                             out_path: str = "reports/history.html") -> str:
    """
    Read the JSON lookup log and generate a styled HTML report.

    Args:
        log_path (str): Path to the JSON log file.
        out_path (str): Where to write the HTML report.

    Returns:
        str: Absolute path to the generated report.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Load history
    records = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError):
            records = []

    total = len(records)
    countries = len(set(r.get("country", "") for r in records))
    ips       = len(set(r.get("ip", "")      for r in records))

    rows_html = ""
    for i, r in enumerate(reversed(records), start=1):
        rows_html += f"""
        <tr>
          <td>{i}</td>
          <td><code>{r.get('ip','?')}</code></td>
          <td>{r.get('country','?')} ({r.get('country_code','??')})</td>
          <td>{r.get('city','?')}</td>
          <td>{r.get('isp','?')}</td>
          <td><code>{r.get('latitude','?')}, {r.get('longitude','?')}</code></td>
          <td>{r.get('fetched_at','?')}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>GeoTracker — Lookup History</title>
  <style>
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0a0e1a;
      color: #e2e8f0;
      padding: 40px 32px;
      min-height: 100vh;
    }}
    h1 {{ font-size:1.6rem; color:#00d4ff; margin-bottom:6px; }}
    .sub {{ color:#64748b; font-size:0.85rem; margin-bottom:32px; }}
    .stats {{
      display:flex; gap:20px; margin-bottom:36px; flex-wrap:wrap;
    }}
    .stat-card {{
      background:#111827; border:1px solid #1e3a5f;
      border-radius:10px; padding:16px 24px;
      min-width:140px;
    }}
    .stat-val {{ font-size:1.8rem; font-weight:700; color:#00d4ff; }}
    .stat-label {{ font-size:0.72rem; color:#64748b; text-transform:uppercase;
                   letter-spacing:0.1em; margin-top:2px; }}
    table {{
      width:100%; border-collapse:collapse;
      font-size:0.82rem; background:#111827;
      border-radius:12px; overflow:hidden;
      border:1px solid #1e3a5f;
    }}
    thead tr {{ background:#0a0e1a; }}
    th {{
      padding:12px 16px; text-align:left;
      font-size:0.68rem; text-transform:uppercase;
      letter-spacing:0.1em; color:#64748b;
      border-bottom:1px solid #1e3a5f;
    }}
    td {{ padding:11px 16px; border-bottom:1px solid rgba(30,58,95,0.5); }}
    tr:last-child td {{ border-bottom:none; }}
    tr:hover td {{ background:rgba(0,212,255,0.04); }}
    code {{
      font-family:'Courier New',monospace;
      font-size:0.8rem; color:#00d4ff;
    }}
    .empty {{ text-align:center; padding:48px; color:#64748b; }}
    footer {{ margin-top:40px; font-size:0.72rem; color:#64748b; text-align:center; }}
  </style>
</head>
<body>
  <h1>🌍 GeoTracker — Lookup History</h1>
  <p class="sub">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-val">{total}</div>
      <div class="stat-label">Total Lookups</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{ips}</div>
      <div class="stat-label">Unique IPs</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{countries}</div>
      <div class="stat-label">Countries</div>
    </div>
  </div>

  {'<table><thead><tr><th>#</th><th>IP Address</th><th>Country</th><th>City</th><th>ISP</th><th>Coordinates</th><th>Fetched At</th></tr></thead><tbody>' + rows_html + '</tbody></table>' if records else '<div class="empty">No lookups recorded yet. Run a lookup first.</div>'}

  <footer>GeoTracker · Powered by ip-api.com</footer>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(out_path)
