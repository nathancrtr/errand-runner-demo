"""One URL as plain text: a web page, a PDF, or a docx. Trimmed, because the
model reads it and an agenda packet can run to hundreds of pages."""

from __future__ import annotations

import html
import io
import ipaddress
import re
import socket
import zipfile
from urllib.parse import urlparse

from .cache import fetch


def public(url: str) -> bool:
    """True for an http(s) URL whose host is on the public internet, so the model can't
    use `errand read` to reach anything on this machine or network."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    try:
        return all(ipaddress.ip_address(info[4][0]).is_global
                   for info in socket.getaddrinfo(u.hostname, None))
    except (OSError, ValueError):
        return False


def read(url: str, words: int = 3000) -> str:
    if not public(url):
        raise SystemExit("errand read: only public http(s) addresses, nothing on this machine or network")
    data, ctype = fetch(url)
    head = data[:8]
    if head.startswith(b"%PDF"):
        from pypdf import PdfReader
        text = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
    elif head.startswith(b"PK") or url.lower().endswith(".docx"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        text = html.unescape(re.sub(r"<[^>]+>", " ", xml.replace("</w:p>", "\n")))
    elif "html" in ctype or b"<html" in data[:2000].lower():
        s = data.decode("utf-8", "replace")
        s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
        text = html.unescape(re.sub(r"<[^>]+>", " ", s))
    else:
        text = data.decode("utf-8", "replace")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    parts = text.split(" ")
    return " ".join(parts[:words]) + (f"\n[... trimmed to {words} words]" if len(parts) > words else "")
