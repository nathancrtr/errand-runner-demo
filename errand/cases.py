"""Rezoning cases near home, from the city's open-data layer. The distance is
computed here from the case boundary, because the server-side buffer was not
trustworthy when checked."""

from __future__ import annotations

import datetime as dt
import json
import math
from urllib.parse import urlencode

from .cache import fetch


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(a))


def cases(watch: dict, home: tuple[float, float], radius_km: float | None = None,
          status: str = "In Process") -> list[dict]:
    radius = radius_km or watch.get("radius_km", 1.5)
    q = urlencode({"where": f"STATUS='{status}'" if status else "1=1",
                   "outFields": "ZONE_CASE,Location,Acres,PrevZoning,ZON_REQ,STATUS,StatusDate,CurrentInfoLink,CASE_TYPE",
                   "returnGeometry": "true", "outSR": 4326, "f": "json"})
    data = json.loads(fetch(f"{watch['cases']['service']}/query?{q}")[0])
    out = []
    for f in data.get("features", []):
        rings = (f.get("geometry") or {}).get("rings") or []
        pts = [p for ring in rings for p in ring]
        if not pts:
            continue
        lon = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        km = _haversine_km(home[0], home[1], lat, lon)
        if km > radius:
            continue
        a = f["attributes"]
        out.append({"case": a["ZONE_CASE"], "location": a.get("Location") or "", "acres": a.get("Acres"),
                    "from": a.get("PrevZoning") or "", "to": a.get("ZON_REQ") or "", "status": a.get("STATUS") or "",
                    "status_date": dt.datetime.fromtimestamp(a["StatusDate"] / 1000, dt.UTC).date().isoformat() if a.get("StatusDate") else "",
                    "distance_km": round(km, 2), "info": a.get("CurrentInfoLink") or ""})
    return sorted(out, key=lambda c: c["distance_km"])
