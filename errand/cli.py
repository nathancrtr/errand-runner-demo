"""errand: three read-only commands, each printing JSON. See ERRAND.md."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path

import requests


def load_env(path: Path = Path(".env")) -> None:
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def home() -> tuple[float, float]:
    try:
        return float(os.environ["HOME_LAT"]), float(os.environ["HOME_LON"])
    except (KeyError, ValueError):
        raise SystemExit("set HOME_LAT and HOME_LON in .env (see .env.example)")


def main(argv: list[str] | None = None) -> None:
    load_env()
    watch = tomllib.loads(Path("watch.toml").read_text())
    p = argparse.ArgumentParser(prog="errand", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("meetings", help="upcoming meetings with agenda items and attachments")
    m.add_argument("--days", type=int, default=None, help="look-ahead window; default from watch.toml")
    r = sub.add_parser("read", help="a page, PDF, or docx as plain text")
    r.add_argument("url")
    r.add_argument("--words", type=int, default=3000)
    c = sub.add_parser("cases", help="rezoning cases near home")
    c.add_argument("--radius", type=float, default=None, help="km; default from watch.toml")
    c.add_argument("--status", default="In Process", help="'' for any status")
    a = p.parse_args(argv)
    try:
        run(a, watch)
    except requests.RequestException as exc:
        raise SystemExit(f"could not fetch: {exc}")


def run(a: argparse.Namespace, watch: dict) -> None:
    if a.cmd == "meetings":
        from .meetings import meetings
        json.dump(meetings(watch, a.days), sys.stdout, indent=1)
    elif a.cmd == "read":
        from .read import read
        print(read(a.url, a.words))
    elif a.cmd == "cases":
        from .cases import cases
        json.dump(cases(watch, home(), a.radius, a.status), sys.stdout, indent=1)
    print()
