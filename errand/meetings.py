"""Upcoming meetings, with every agenda item and its attachments, from two vendors:
eSCRIBE (Raleigh) and the Legistar Web API (Wake County). Both public, no keys."""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from urllib.parse import quote

from .cache import fetch

LEGISTAR = "https://webapi.legistar.com/v1"


def _text(fragment: str, limit: int = 700) -> str:
    s = re.sub(r"<[^>]+>", " ", fragment)
    s = re.sub(r"\s+", " ", html.unescape(s)).strip()
    return s[:limit]


def _escribe_items(site: str, url: str) -> list[dict]:
    page = fetch(url)[0].decode("utf-8", "replace")
    starts = [m.start() for m in re.finditer(r'<div class="AgendaItem AgendaItem\d+ "', page)]
    items = []
    for i, start in enumerate(starts):
        block = page[start:starts[i + 1] if i + 1 < len(starts) else None]
        title = re.search(r'class="AgendaItemTitle".*?<a [^>]*>(.*?)</a>', block, re.S)
        counter = re.search(r'class="AgendaItemCounter">(.*?)</div>', block, re.S)
        desc = re.search(r'class="AgendaItemDescription RichText">(.*?)</div></div></div>', block, re.S)
        atts = [{"name": _text(n, 120), "url": f"{site}/{html.unescape(href)}"}
                for href, n in re.findall(r'href="(FileStream\.ashx\?DocumentId=\d+)"[^>]*>(.*?)</a>', block, re.S)]
        if title:
            items.append({"number": _text(counter.group(1), 10) if counter else "",
                          "title": _text(title.group(1), 200),
                          "description": _text(desc.group(1)) if desc else "",
                          "attachments": atts})
    return items


def escribe(body: dict, start: dt.date, end: dt.date) -> list[dict]:
    site = body["site"]
    raw = fetch(f"{site}/MeetingsCalendarView.aspx/GetCalendarMeetings", method="POST",
                body={"calendarStartDate": start.isoformat(), "calendarEndDate": end.isoformat()},
                headers={"Content-Type": "application/json; charset=utf-8"})[0]
    out = []
    for m in json.loads(raw)["d"]:
        if body["match"].lower() not in m["MeetingName"].lower():
            continue
        url = f"{site}/Meeting.aspx?Id={m['ID']}&Agenda=Agenda&lang=English"
        out.append({"body": body["name"], "id": m["ID"], "title": html.unescape(m["MeetingName"]),
                    "start": dt.datetime.strptime(m["StartDate"][:16], "%Y/%m/%d %H:%M").isoformat(),
                    "location": html.unescape(m.get("Location") or ""), "url": url,
                    "items": _escribe_items(site, url) if m.get("HasAgenda") else []})
    return out


def legistar(body: dict, start: dt.date, end: dt.date) -> list[dict]:
    base = f"{LEGISTAR}/{body['client']}"
    flt = quote(f"EventDate ge datetime'{start}' and EventDate le datetime'{end}'")
    events = json.loads(fetch(f"{base}/events?$filter={flt}&$orderby=EventDate")[0])
    out = []
    for e in events:
        if body["match"].lower() not in (e.get("EventBodyName") or "").lower():
            continue
        raw = fetch(f"{base}/events/{e['EventId']}/eventitems?AgendaNote=1&MinutesNote=1&Attachments=1")[0]
        items = [{"number": it.get("EventItemAgendaNumber") or "",
                  "title": (it.get("EventItemTitle") or "").strip(),
                  "description": (it.get("EventItemAgendaNote") or "")[:700],
                  "attachments": [{"name": a.get("MatterAttachmentName") or "", "url": a.get("MatterAttachmentHyperlink") or ""}
                                  for a in it.get("EventItemMatterAttachments") or []]}
                 for it in json.loads(raw) if (it.get("EventItemTitle") or "").strip()]
        when = e["EventDate"][:10]
        try:
            t = dt.datetime.strptime(e.get("EventTime") or "", "%I:%M %p").time()
        except ValueError:
            t = dt.time(0, 0)
        out.append({"body": body["name"], "id": str(e["EventId"]), "title": e["EventBodyName"],
                    "start": dt.datetime.combine(dt.date.fromisoformat(when), t).isoformat(),
                    "location": e.get("EventLocation") or "", "url": e.get("EventInSiteURL") or "",
                    "agenda_pdf": e.get("EventAgendaFile") or "", "items": items})
    return out


def meetings(watch: dict, days: int | None = None) -> list[dict]:
    start = dt.date.today()
    end = start + dt.timedelta(days=days or watch.get("days_ahead", 14))
    out = []
    for body in watch["body"]:
        out += {"escribe": escribe, "legistar": legistar}[body["source"]](body, start, end)
    return sorted(out, key=lambda m: m["start"])


def listing(ms: list[dict]) -> str:
    """One line per item: what a reader needs to decide whether to look closer."""
    out = []
    for m in ms:
        out.append(f"# {m['body']} | {m['title']} | {m['start'][:16]} | {m['location']} | id={m['id']}")
        for it in m["items"]:
            desc = f" — {it['description'][:110]}" if it["description"] else ""
            att = f" [{len(it['attachments'])} att]" if it["attachments"] else ""
            out.append(f"{it['number']} {it['title']}{desc}{att}")
        if not m["items"]:
            out.append("(no agenda posted yet)")
    return "\n".join(out)


def item(ms: list[dict], meeting_id: str, number: str) -> str:
    for m in ms:
        if m["id"] == meeting_id:
            for it in m["items"]:
                if it["number"].rstrip(".") == number.rstrip("."):
                    atts = "\n".join(f"- {a['name']}: {a['url']}" for a in it["attachments"]) or "(none)"
                    return f"{it['number']} {it['title']}\n\n{it['description']}\n\nAttachments:\n{atts}"
            raise SystemExit(f"no item {number} in meeting {meeting_id}")
    raise SystemExit(f"no meeting with id {meeting_id}")
