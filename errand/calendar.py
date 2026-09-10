"""The one writer: an event appended to data/council.ics, keyed by UID so a
second run with the same meeting changes nothing. Never removes or edits."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

ICS = Path("data/council.ics")
HEADER = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//errand//council watcher//EN\nX-WR-CALNAME:Council\n"


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _stamp(iso: str) -> str:
    return dt.datetime.fromisoformat(iso).strftime("%Y%m%dT%H%M%S")


def add(uid: str, start: str, end: str, summary: str, location: str, description: str) -> str:
    text = ICS.read_text() if ICS.exists() else HEADER + "END:VCALENDAR\n"
    if f"UID:{uid}\n" in text:
        return f"already there: {uid}"
    event = (f"BEGIN:VEVENT\nUID:{uid}\nDTSTAMP:{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}\n"
             f"DTSTART:{_stamp(start)}\nDTEND:{_stamp(end)}\nSUMMARY:{_esc(summary)}\n"
             f"LOCATION:{_esc(location)}\nDESCRIPTION:{_esc(description)}\nEND:VEVENT\n")
    ICS.parent.mkdir(exist_ok=True)
    ICS.write_text(text.replace("END:VCALENDAR\n", event + "END:VCALENDAR\n"))
    return f"added: {uid}"


def listing() -> str:
    if not ICS.exists():
        return "(no calendar yet)"
    out, cur = [], {}
    for line in ICS.read_text().splitlines():
        if line == "END:VEVENT":
            out.append(f"{cur.get('DTSTART', '')[:13]} {cur.get('SUMMARY', '')}  [{cur.get('UID', '')}]")
            cur = {}
        elif ":" in line:
            k, v = line.split(":", 1)
            cur[k] = v
    return "\n".join(out) or "(no events)"
