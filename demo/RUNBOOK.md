# Runbook: the live build

Open this file somewhere the audience can't see it. The demo happens in a separate
clone so the tagged repo stays pristine:

```sh
git clone ~/repos/errand-runner-demo ~/demo/errand-runner-demo && cd ~/demo/errand-runner-demo
git checkout -b live stage-0                 # ERRAND.md, PROFILE.md, watch.toml are already there
git checkout main -- watch.toml && git commit -qm "Stage 0: where things are published"   # the builder's crumbs
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
cache is offline by construction. That holds for the second terminal only: run stage-3
there Thursday night, and on Friday its run reads the same agendas whether or not the
Wi-Fi holds. The live build starts with an empty cache, and the live-built tool may key
its calendar lookup on today's date, so Prompt 1 needs the network in the room. If the
Wi-Fi is down, go straight to the second terminal.

Two sources the model may hit and cannot read: `raleighnc.gov` sits behind a Cloudflare
challenge that blocks scripts, and the case-detail links in the open-data layer point
there. A good run says "couldn't open it" and moves on. Watch that it does.

## What's there right now (checked 2026-09-10)

- The 2026-09-15 City Council agenda has 83 items and 190 attachments. Rehearsed
  three times; every run found the same two things: **F.2, rezoning Z-22-26 at Bragg
  and South East Streets**, 1.2 km from home, removing a neighborhood conservation
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
- Open-data rezoning cases in process within 1.5 km of the demo home point (Moore
  Square): the Wilmington Street assemblage (1.05 km), Bragg & S East (1.21), 767 S
  Saunders St (1.3), and 727 W Morgan St (1.48).
- The 2026-09-15 meeting shows as 11:03 in Raleigh's calendar though its name says
  11:30am. watch.toml says to trust the name; check the .ics time after Prompt 3.
- The Planning Commission did not appear in the next five weeks of the eSCRIBE calendar.
  Not in scope, but have an answer if someone asks.

## Timings (25 minutes on the build)

| min | stage | what the room sees | while it runs, say |
|---|---|---|---|
| 0-3 | 0 | `cat ERRAND.md`, `cat PROFILE.md`. Two files, plain English. Open Claude Code from the clone: `cd ~/demo/errand-runner-demo && claude --effort medium`. Started from `~`, it searched the home folder and named the finished repos on screen. | "The first is the job. The second is the taste. Neither is code." |
| 3-10 | 1 | Prompt 1. Model writes the read-only tools. `errand meetings \| head -40`, `errand cases`. | Did it find eSCRIBE and Legistar, or invent an API? Where's the home coordinate going? |
| 10-18 | 2 | Prompt 2. `errand run`, about 45 seconds. The trace scrolls: which items it opened, which it skipped. Then the digest. | This is the agentic part. The tool count wasn't known until it ran. The policy that governed it is the paragraph you read at minute one. |
| 18-23 | 3 | Prompt 3. `errand run` again, now with the writer allowed. `cat data/council.ics`, `open data/council.ics`. Run once more: the file doesn't change. | The leash: one write tool, "add only, never remove", and the file is the proof. |
| 23-25 | | Swap: someone names their neighborhood. Edit two lines of .env and one paragraph of PROFILE.md. Run again. | "Different city is one block of watch.toml, if it's on Legistar or eSCRIBE." |

## Prompts to type

Type these more or less verbatim. They are in plain words on purpose: the point for the
room is that the person asking never had to know what an API is. The crumbs a builder
needs, where each agenda is published and which flag pins the leash, are comments in
`watch.toml`, which the first prompt tells the model to read. Say that out loud: the
plumbing is written down in the config file, and it is still not code.

**Prompt 1 (stage 1: the tools)**

> Read ERRAND.md. Before anything reads the agendas for me, I want a few small commands
> I can run myself, so I can see what it sees. They should let me do the following and
> no more for now:
>
> - List the upcoming meetings and what's on each agenda
> - Show a single agenda item in full
> - Open an attachment or a web page as plain text
> - List rezoning cases near my home
>
> My details are in `watch.toml` and `.env`. Keep the agenda listing short enough to read
> in one sitting, and save everything you download so a second run doesn't need the
> internet. Call the tool `errand`, keep it small and plain, and Python is fine.

**Prompt 2 (stage 2: the policy)**

> Now do the errand itself. Add `errand run`: it hands those commands to Claude, along
> with ERRAND.md and PROFILE.md, and lets it read the agendas the way I would: skim the
> list, open an item only when the title isn't enough, look up a case only when it has
> to. It may use those commands and nothing else on my computer. When it's done, print
> a short digest: the meetings that matter, one line each on why, then what it checked
> and what it skipped. Save the digest, and keep a record of what it chose to open so I
> can see it.

**Prompt 3 (stage 3: the leash and the clock)**

> Two more things. First, let it put meetings on my calendar, but only one way: it may
> add a meeting to a calendar file I can open on my Mac, with the why-line in the
> description, and it must never remove or change anything. Adding the same meeting
> twice should do nothing. Second, make this happen on its own every Friday morning at
> 7:45, and keep a log.

## What to say when it's slow

Expect one quiet stretch in Prompt 1: after the model has looked at the three sources
and before the file appears, it plans the whole tool in one turn with nothing on screen
but the spinner. At default effort on 2026-09-10 that was 3 minutes, then 80 seconds to
write the file. Output speed is about 77 tokens a second, so the wait is set by how much
it thinks and writes, not by the network. That stretch is the time to use these.

- Nobody had to write a spec. The three prompts are the errand said three times, each
  time asking for a little more. The technical crumbs went in the config file.
- Build-time AI wrote the tools and is gone. Run-time AI reads the agenda every Friday
  and decides what to open. Both are in this room; only the second is "agentic".
- The leash has three parts and all of them are readable: the allowed-tools list and
  the hook that enforces it, the paragraph in PROFILE.md, and "add only, never remove" in the policy.
- The trace is the point. Run it twice with two neighborhoods and the tool calls differ.
- Two sources, two vendors, no keys. Legistar covers hundreds of cities; eSCRIBE covers
  hundreds more. Most people in the room can swap in their own city in one block.
- If someone asks whether the leash is real: `errand run` is a nested Claude Code whose
  only tool is Bash, with a hook that refuses any command that isn't one `errand`
  command. In the live rehearsal the builder asked it to run `ls ~`, `cat .env` and
  `errand cases && cat .env`, and the hook refused all three. That is the rule, and it
  is checkable.

## What went wrong last time (2026-09-10 rehearsal)

Name one of these when the room asks.

- **The leash was loose until it wasn't.** With only `--allowedTools`, the nested model
  inherited this machine's "auto" permission mode and a classifier approved a `touch`
  the list never named. `--permission-mode default` closed that, but not all the way:
  default mode still lets read-only commands (`ls`, `cat`) and the Read tool through
  without asking, so the nested model could read `.env`. The live build found this by
  testing, and closed it with `--tools Bash` and a PreToolUse hook. The recipe is now in
  watch.toml, and the stage-2 and stage-3 tags carry it too (`errand/guard.py`), so
  the fallback terminal's leash is the same one.
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
