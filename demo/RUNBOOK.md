# Runbook: the live build

Open this file somewhere the audience can't see it. The demo happens in a separate
clone so the tagged repo stays pristine:

```sh
git clone ~/repos/errand-runner-demo ~/demo/errand-runner-demo && cd ~/demo/errand-runner-demo
git checkout -b live stage-0                 # ERRAND.md, PROFILE.md, watch.toml are already there
uv venv && uv pip install requests pypdf     # so the venv exists before the room watches
cp ~/repos/errand-runner-demo/.env .env      # HOME_LAT and HOME_LON, nothing else
```

`.env` is the only private thing in this build, and it holds two numbers. The exact
address never goes in a file the room sees: PROFILE.md says "Warehouse District,
District C", and that is all the model needs.

The build is three stages, and they are not the fetch/filter/remember of a plain
script, because the model runs at run time with tools: **tools, then policy, then the
leash and the clock.**

## Safety net

Each tag is what the live build should have produced by that point, rehearsed on
2026-09-10. If the model wanders or the network dies, park the live work and jump:

```sh
git stash -u && git checkout stage-1    # or stage-2, stage-3
uv pip install -e .
```

Keep a second terminal on `~/repos/errand-runner-demo` with stage-3 installed, `.env`
filled, and an `errand run --dry-run` already scrolled to the top of the screen. Record
a screen capture of a full run-through tonight as the last resort.

There is no fixture; the model chooses what to read, so a canned response would be a
lie. Instead, stage 1 caches every download under `data/cache/`, and a run with a warm
cache is offline by construction. Run the whole thing Thursday night, and on Friday the
room's run reads the same agendas whether or not the Wi-Fi holds.

Two sources the model may hit and cannot read: `raleighnc.gov` sits behind a Cloudflare
challenge that blocks scripts, and the case-detail links in the open-data layer point
there. A good run says "couldn't open it" and moves on. Watch that it does.

## What's there right now (checked 2026-09-10)

- The 2026-09-15 City Council agenda has 83 items and 190 attachments. Rehearsed
  three times; every run found the same two things: **F.2, rezoning Z-22-26 at Bragg
  and South East Streets**, 1.24 km from home, removing a neighborhood conservation
  overlay, and **D.5.d, a Complete Streets contract for Harrington, West, and Cabarrus
  Streets**, inside the Warehouse District. Every run set aside the City Hall and City
  Center parking-deck items with the reason PROFILE.md gives, and the annexations and
  rezonings in Districts A, B, and D as elsewhere.
- Inside item F, the agenda forecasts six rezoning hearings for October 6, two in
  District C. One, Z-50-25 on Capital Boulevard, is about 3 km from home: inside the
  district, outside the neighborhood. If it comes up, that is the "wiggle room" test.
- A run takes 40 to 50 seconds with a warm cache and makes three or four tool calls.
- The 2026-09-08 county agenda had 52 items, including an affordable-housing loan at
  450 East Davie Street, a short walk away. The county posts the next agenda a few days
  before the meeting, so check on Thursday whether there is one.
- Open-data rezoning cases in process near the neighborhood: 767 S Saunders St, the
  Wilmington Street assemblage, 727 W Morgan St, and Ashe Avenue.
- The Planning Commission did not appear in the next five weeks of the eSCRIBE calendar.
  Not in scope, but have an answer if someone asks.

## Timings (25 minutes on the build)

| min | stage | what the room sees | while it runs, say |
|---|---|---|---|
| 0-3 | 0 | `cat ERRAND.md`, `cat PROFILE.md`. Two files, plain English. Open Claude Code. | "The first is the job. The second is the taste. Neither is code." |
| 3-10 | 1 | Prompt 1. Model writes the read-only tools. `errand meetings \| head -40`, `errand cases`. | Did it find eSCRIBE and Legistar, or invent an API? Where's the home coordinate going? |
| 10-18 | 2 | Prompt 2. `errand run`, about 45 seconds. The trace scrolls: which items it opened, which it skipped. Then the digest. | This is the agentic part. The tool count wasn't known until it ran. The policy that governed it is the paragraph you read at minute one. |
| 18-23 | 3 | Prompt 3. `errand run` again, now with the writer allowed. `cat data/council.ics`, `open data/council.ics`. Run once more: the file doesn't change. | The leash: one write tool, "add only, never remove", and the file is the proof. |
| 23-25 | | Swap: someone names their neighborhood. Edit two lines of .env and one paragraph of PROFILE.md. Run again. | "Different city is one block of watch.toml, if it's on Legistar or eSCRIBE." |

## Prompts to type

Type these more or less verbatim. They're written so a non-engineer can follow what is
being asked.

**Prompt 1 (stage 1: the tools)**

> Read ERRAND.md and watch.toml. Build a small Python command-line tool called
> `errand` with three read-only commands that print JSON. `errand meetings` lists the
> meetings in the next `days_ahead` days for each body in watch.toml, with every agenda
> item's title and attachment links. Raleigh City Council is on eSCRIBE: POST to
> MeetingsCalendarView.aspx/GetCalendarMeetings for the calendar, then read each
> meeting's Agenda HTML page. Wake County is on the Legistar Web API, client `wake`:
> events, then eventitems with Attachments=1. Print the listing compactly, one line
> per item with the start of its description, because a model will read it and one
> agenda is eighty items; add `errand item <meeting-id> <number>` for one item in full
> with its attachment links. `errand read <url>` prints a web page, PDF, or docx as
> plain text, trimmed to a few thousand words. `errand cases` lists
> rezoning cases from the open-data layer in watch.toml that are within `radius_km` of
> HOME_LAT and HOME_LON in .env, with the distance computed here, not by the server.
> Cache every download under data/cache so a second run works offline. Keep it under
> 250 lines, plain `requests` plus `pypdf`, no framework. Use uv and a pyproject with
> an `errand` script.

**Prompt 2 (stage 2: the policy)**

> Now make the errand real, but read-only. Add `errand run`: build a prompt from
> ERRAND.md, PROFILE.md, and watch.toml and run it through `claude -p` with
> `--permission-mode default` and `--allowedTools` limited to `Bash(errand meetings*)`,
> `Bash(errand item*)`, `Bash(errand read*)`, and `Bash(errand cases*)`. The policy in
> the prompt: call `errand meetings` once; for
> each item decide whether it could be about my neighborhood; open an attachment or
> look up a case only when the title isn't enough; and finish with a short digest: the
> meetings that matter, one line each on why, then a "what I checked and skipped" list.
> Print the digest and save it to data/last-digest.md. Save the model's tool calls to
> data/last-trace.txt so I can see what it chose to open.

**Prompt 3 (stage 3: the leash and the clock)**

> Two more things. First, add `errand calendar add`: it appends an event to
> data/council.ics with a stable UID built from the meeting, the meeting's start time
> and place, and the why-line as the description, and does nothing if that UID is
> already in the file. Allow it in `errand run`, and add to the policy: add only the
> meetings that matter, never remove or edit anything. Second, schedule it: a launchd
> plist and an install script so this runs every Friday at 7:45 and logs to data/.

## What to say when it's slow

- Build-time AI wrote the tools and is gone. Run-time AI reads the agenda every Friday
  and decides what to open. Both are in this room; only the second is "agentic".
- The leash has three parts and all of them are readable: the allowed-tools list, the
  paragraph in PROFILE.md, and "add only, never remove" in the policy.
- The trace is the point. Run it twice with two neighborhoods and the tool calls differ.
- Two sources, two vendors, no keys. Legistar covers hundreds of cities; eSCRIBE covers
  hundreds more. Most people in the room can swap in their own city in one block.
- If someone asks whether the leash is real: `errand run` is a nested Claude Code with
  four allowed command prefixes. In rehearsal it was asked to `touch` a file and was
  blocked; `errand cases; touch x` was blocked as a whole. Harmless glue like `echo` and
  `| head` passes. That is the rule, and it is checkable.

## What went wrong last time (2026-09-10 rehearsal)

Name one of these when the room asks.

- **The leash was loose until it wasn't.** With only `--allowedTools`, the nested model
  inherited this machine's "auto" permission mode and a classifier approved a `touch`
  the list never named. `--permission-mode default` closed it. That flag is now in
  Prompt 2 and in the code.
- **The first `errand meetings` printed everything as JSON,** over 100 KB for one
  agenda, which is more than a nested model gets to see from one command. Compact
  listing plus `errand item` fixed it.
- **eSCRIBE timestamps carry seconds** and the first parse crashed on them.
- **The county board had no meeting in the window.** Wake County posts the agenda a few
  days ahead; check Thursday whether one exists, and if not, say the quiet source is the
  normal case.

## Showing the calendar

`open data/council.ics` imports into Calendar.app and shows the events. For a
subscription that refreshes, run `python -m http.server 8765 --directory data` in the
second terminal and subscribe Calendar.app to `http://localhost:8765/council.ics`.
Either way, the diff of the file after a second run is the idempotence proof, and it is
easier to see than the calendar.

## If someone in the room has a better errand

Same three prompts. A different neighborhood is two lines of `.env` and a paragraph of
PROFILE.md. A different city is one block of `watch.toml`, if it publishes to Legistar
or eSCRIBE; check with one curl before promising. A different errand altogether means
different tools in stage 1, and the shape from stage 2 on holds.
