"""The errand itself. A model reads the agendas with the read-only tools, under a
policy written in prose, and produces the digest. The trace of what it chose to
open is saved beside the digest, because the choosing is the point."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = ["Bash(errand meetings*)", "Bash(errand item*)", "Bash(errand read*)", "Bash(errand cases*)"]

POLICY = """You are running an errand for one person. The errand and the person are described
below. Do the errand and write the digest; nothing else.

Tools, run through Bash exactly as shown, one per call. Anything else is refused,
including pipes, `&&`, `head` and every other program:
  errand meetings                          upcoming meetings, one line per agenda item
  errand item <meeting-id> <item-number>   one item in full: description and attachment links
  errand read '<url>'                      an attachment or page as plain text (quote the URL)
  errand cases                             rezoning cases in process near home, with distance in km

Policy:
1. Call `errand meetings` once.
2. For each agenda item, decide from its line whether it could be about this person's
   neighborhood. Citywide policy, contracts and projects elsewhere, proclamations, and
   items placed in other parts of town need no second look.
3. When a line is not enough to decide (a street you cannot place, a case number,
   "downtown"), call `errand item`, and only if still unsure `errand read` one attachment
   or `errand cases`. Open as little as it takes.
4. Some links, especially raleighnc.gov, cannot be fetched. Say so and move on.
5. Finish with the digest in markdown, under 25 lines:
   ## Meetings that matter
   One bullet per meeting: date, time, place, then its items with one line each on why
   they matter to this person. Leave out meetings with nothing that matters.
   ## Checked and skipped
   What you opened, and the items you considered but set aside, each with the reason in
   a few words.
   If nothing near home is on any agenda, say so in one line and stop.

THE ERRAND:
{errand}

THE PERSON:
{profile}

WATCHING: {bodies}, {days} days ahead, "neighborhood" means within {radius} km of home.
"""


def run(watch: dict, timeout: int = 900) -> None:
    if not shutil.which("claude"):
        raise SystemExit("the claude CLI is not installed; the errand needs it to read agendas")
    prompt = POLICY.format(
        errand=Path("ERRAND.md").read_text(), profile=Path("PROFILE.md").read_text(),
        bodies=", ".join(b["name"] for b in watch["body"]),
        days=watch.get("days_ahead", 14), radius=watch.get("radius_km", 1.5))
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    env["PATH"] = f"{Path(sys.executable).parent}:{env.get('PATH', '')}"
    # The leash. --permission-mode default: without it the machine's own mode applies, and
    # in "auto" mode a classifier waves through writes the allowed-tools list never named.
    # Default mode still lets `ls` and `cat` through, so Bash is the only tool, this
    # machine's settings and MCP servers are ignored, and guard.py refuses every command
    # that isn't one errand command.
    guard = f"'{sys.executable}' '{Path(__file__).with_name('guard.py')}'"
    hooks = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": guard}]}]}}
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "default", "--tools", "Bash", "--setting-sources", "",
           "--strict-mcp-config", "--settings", json.dumps(hooks),
           "--max-turns", "40", "--allowedTools", *TOOLS]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    trace, digest = [], ""
    for line in proc.stdout:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for block in ev["message"].get("content", []):
                if block.get("type") == "tool_use":
                    call = block["input"].get("command") or json.dumps(block["input"])
                    trace.append(call)
                    print(f"  → {call}", file=sys.stderr, flush=True)
        elif ev.get("type") == "result":
            digest = ev.get("result") or ""
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise SystemExit("the model ran out of time")
    if proc.returncode != 0 or not digest:
        raise SystemExit(f"claude exited {proc.returncode}: {proc.stderr.read()[:500]}")
    Path("data").mkdir(exist_ok=True)
    Path("data/last-digest.md").write_text(digest + "\n")
    Path("data/last-trace.txt").write_text("\n".join(trace) + "\n")
    print(f"\n{digest}\n\n({len(trace)} tool calls; trace in data/last-trace.txt)")
