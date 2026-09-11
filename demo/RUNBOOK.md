# Runbook: the live build

Open this file somewhere the audience can't see it.

## Before the room

- [ ] The 2026-09-15 Council meeting is still ahead of today. If the demo is after it,
      "What's there right now" is stale: run `errand meetings` in the fallback terminal
      and re-pick the two items to expect.
- [ ] Fresh demo clone, made with the block below. Move any earlier clone aside first.
- [ ] Fallback terminal on its own clone, so this repo (runbook, slides) stays on main:
      `git clone ~/repos/errand-runner-demo ~/demo/fallback && cd ~/demo/fallback && git checkout stage-3`,
      `uv venv && uv pip install -e . && cp ~/repos/errand-runner-demo/.env .`, then
      `.venv/bin/errand run --dry-run` to warm the cache; leave it scrolled to the top.
- [ ] Slides open from `~/repos/errand-runner-demo/demo/slides.html`, one keystroke from
      the terminal. Terminal font big enough for the back row.
- [ ] `claude` is logged in, the Wi-Fi works, notifications are off.
- [ ] A screen recording of a full run-through exists, as the last resort.

The demo happens in a separate clone so the tagged repo stays pristine:

```sh
mv ~/demo/errand-runner-demo ~/demo/errand-runner-demo.old-$(date +%H%M) 2>/dev/null   # a rehearsal's clone
launchctl bootout gui/$(id -u)/com.nathancarter.errand 2>/dev/null; rm -f ~/Library/LaunchAgents/com.nathancarter.errand.plist   # a rehearsal's Friday job
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
2026-09-10; stage-2 and stage-3 gained the leash hook on 2026-09-11. If the model
wanders or the network dies, park the live work and jump:

```sh
git stash -u && git checkout stage-1    # or stage-2, stage-3
uv pip install -e .
```

Keep a second terminal on `~/demo/fallback` with stage-3 installed, `.env` filled, and
an `errand run --dry-run` already scrolled to the top of the screen (see the checklist).

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

## What's there right now (checked 2026-09-11)

- The 2026-09-15 City Council agenda has 83 items and 190 attachments. Rehearsed
  five times; every run found the same two things: **F.2, rezoning Z-22-26 at Bragg
  and South East Streets**, 1.2 km from home, removing a neighborhood conservation
  overlay, and **D.5.d, a Complete Streets contract for Harrington, West, and Cabarrus
  Streets**, inside the Warehouse District. Every run set aside the City Hall and City
  Center parking-deck items with the reason PROFILE.md gives, and the annexations and
  rezonings in Districts A, B, and D as elsewhere.
- Inside item F, the agenda forecasts six rezoning hearings for October 6, two in
  District C. One, Z-50-25 on Capital Boulevard, is about 3 km from home: inside the
  district, outside the neighborhood. If it comes up, that is the "wiggle room" test.
- A run takes 40 to 70 seconds and makes 6 to 13 tool calls, depending on how many
  items it opens.
- The Wake County board has no meeting in the window as of 2026-09-11. The 2026-09-08
  agenda had an affordable-housing loan at 450 East Davie Street, a short walk away. The
  county posts agendas a few days ahead; if none is up, the quiet source is the normal case.
- Open-data rezoning cases in process within 1.5 km of the demo home point (Moore
  Square): the Wilmington Street assemblage (1.05 km), Bragg & S East (1.21), 767 S
  Saunders St (1.3), and 727 W Morgan St (1.48).
- The 2026-09-15 meeting shows as 11:03 in Raleigh's calendar though its name says
  11:30am. watch.toml says to trust the name, and the rehearsal's event said 11:30. Both
  items sit in the 1:00 PM afternoon session; the digest says so, the event doesn't.
- The Planning Commission did not appear in the next five weeks of the eSCRIBE calendar.
  Not in scope, but have an answer if someone asks.

## Timings (25 minutes on the build)

Rehearsed at medium effort on 2026-09-11: Prompt 1 3m43s, Prompt 2 3m35s, Prompt 3
4m06s. About 11 minutes of model time; the slack goes to the swap. Run your own
commands inside Claude Code with `!`, e.g. `! .venv/bin/errand cases`.

| min | stage | do | slides | say |
|---|---|---|---|---|
| 0-3 | 0 | Slide 1 up; read the quote. `cat ERRAND.md`, `cat PROFILE.md`. Then `cd ~/demo/errand-runner-demo && claude --effort medium`: from the clone, never from `~`. | 1, then 2 just before typing Prompt 1 | "The first is the job. The second is the taste. Neither is code." Say "medium effort, on purpose" as you type the flag; slide 5 pays it off. |
| 3-9 | 1 | Prompt 1, about 3½ min, with a quiet stretch of a minute or more before the file appears. Then `! .venv/bin/errand meetings \| head -40` and `! .venv/bin/errand cases`. | 3 and 4 during the quiet stretch; terminal once output appears | Did it find eSCRIBE and Legistar, or invent an API? Where's the home coordinate going? |
| 9-15 | 2 | Prompt 2, about 3½ min. **Watch for** its leash test: the leashed Claude is told to `cat .env` and the hook refuses. Point at it. Then the builder runs `errand run` itself, about 60 s: the trace scrolls, then the digest. Expect D.5.d and F.2. | 5 to 7 while it writes; nothing during the run itself | This is the agentic part. The tool count wasn't known until it ran. The policy that governed it is the paragraph you read at minute one. "That's the loop from the diagram, going around." |
| 15-21 | 3 | Prompt 3, about 4 min. The builder fires the Friday job once through launchd; that is the run with the writer, about 60 s. `cat` the calendar file it names (`data/meetings.ics` in rehearsal) and `open` it, once. For "twice does nothing", repeat the add command from `data/errand.log` by hand, not a whole run: it says the meeting is already there, and `md5` of the file doesn't move. | 8 and 9 while it writes; slide 9 ends on "then check", which is the cue to go back to the terminal | The leash: one write tool, "add only, never remove", and the file is the proof. In rehearsal the model passed only the meeting's tag and the why-line; the date came from the council's listing, so it can't invent a meeting. |
| 21-25 | | Swap: someone names a neighborhood. Its coordinates from Maps (right-click, copy) into the two lines of `.env`; its name into PROFILE.md's first sentence. `! .venv/bin/errand run`, about 60 s. The writer is on, so it may add their meetings to the file. | 10, and leave it up through questions | "Different city is one block of watch.toml, if it's on Legistar or eSCRIBE." |

## Slides and the terminal

`demo/slides.html` is ten slides, labeled by prompt. Each group is what to talk over
while that prompt's model is working. Two exceptions: slide 2 goes up *before* Prompt 1
is typed, so the room knows which of the two AIs it is about to watch, and slide 10 is
the close. Keys: arrows, space, Page Up/Down, F for full screen. The slide number lives
in the URL hash, so switching to the terminal and back never loses the place. Keep
slides and terminal as two windows one keystroke apart.

| slide | title | when |
|---|---|---|
| 1 | Errand runner (the ERRAND.md quote) | As people settle. The `cat ERRAND.md` at minute 0 then reveals the slide was a file. |
| 2 | Two AIs in this room | After Claude Code is open, before Prompt 1 is typed. |
| 3 | What an agent is | Prompt 1 quiet stretch. Refer back to it by voice when `errand run` scrolls. |
| 4 | It only knows what you hand it | Prompt 1 quiet stretch. Primes the check on `errand meetings`. |
| 5 | Not too much model | Prompt 2 wait. Retrospective on the Prompt 1 wait, so never earlier. |
| 6 | Help the model make itself obsolete | Prompt 2 wait. |
| 7 | When all you have is an LLM | Prompt 2 wait. It describes calendar idempotence, which doesn't exist until Prompt 3: say "the next prompt will prove this." |
| 8 | Rules that must hold belong in code | Prompt 3 wait. Depends on the room knowing `.env` exists (see below). |
| 9 | Say what done looks like, then check | Prompt 3 wait, last. "Then check" is the cue for the repeated add and the unchanged `.ics`. |
| 10 | Find your own errand | The swap and the close. Leave it up. |

### Before opening the slides

- The shape in one breath: one sentence of spec, three prompts, twenty-five minutes,
  and the slides are what to think about while the model works.
- Warn about silence: "When the screen stops moving, the model is thinking, and I'll
  talk." Otherwise the first quiet stretch reads as a failure.
- Nothing is canned. The model chooses what to open, so today's digest may differ from
  rehearsal. This buys the credit you need when raleighnc.gov is blocked.

### Before the first prompt

- Say out loud that the plumbing crumbs live in `watch.toml` and are still not code.
  Slide 4 assumes the room already knows.
- Name what is private: two coordinates in `.env`, a file the room will not see.
  Slide 8 depends on the room knowing that file exists.
- Say what a good Prompt 1 looks like before it runs: real data sources, not an invented
  API. Then the check after `errand meetings` is a payoff, not an explanation.

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

Expect one quiet stretch per prompt: the model plans the whole change in one turn with
nothing on screen but the spinner. At medium effort on 2026-09-11 that was about 80
seconds in Prompt 1 (after it looks at the sources, before the file appears), about 60
in Prompt 2, and about 80 right at the start of Prompt 3. At default effort the Prompt 1
stretch was 3 minutes. Output speed is about 77 tokens a second, so the wait is set by
how much it thinks and writes, not by the network. Those stretches are the time to use these.

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
  command. In rehearsal it was asked to run `ls ~`, `cat .env`, `errand cases && cat .env`,
  `errand read "$(cat .env)"` and `touch`, and the hook refused every one. Told to find
  another way into `.env`, it declined. That is the rule, and it is checkable.

## What went wrong in rehearsal (2026-09-10 and 11)

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
- **The guard refused its own reader's URLs.** eSCRIBE attachment links contain `?`, so
  unquoted they looked like shell syntax; the reader was refused three times before it
  quoted them. watch.toml now says to tell it to quote URLs.
- **Started from `~`, the builder searched the home folder** and named the finished repos
  on screen; learning launchd, it printed another project's job. Launching from the clone
  and the launchd crumb in watch.toml fixed both.
- **The county board had no meeting in the window.** Wake County posts the agenda a few
  days ahead; check Thursday whether one exists, and if not, say the quiet source is the
  normal case.

## Showing the calendar

The live build names its own file (`data/meetings.ics` on 2026-09-11); the tags use
`data/council.ics`. `open` imports it into Calendar.app and shows the events, and
opening it again may import them twice, so open it once. For a
subscription that refreshes, run `python -m http.server 8765 --directory data` and
subscribe Calendar.app to `http://localhost:8765/<the file>.ics`. Either way, the file is
the idempotence proof, and it is easier to see than the calendar.

## After the demo

```sh
launchctl bootout gui/$(id -u)/com.nathancarter.errand; rm -f ~/Library/LaunchAgents/com.nathancarter.errand.plist
```

The live build installs a real Friday job pointing at the demo clone; this removes it.
Delete the "Raleigh City Council" events that `open` imported into Calendar.app.

## If someone in the room has a better errand

Same three prompts. A different neighborhood is two lines of `.env` and a paragraph of
PROFILE.md. A different city is one block of `watch.toml`, if it publishes to Legistar
or eSCRIBE; check with one curl before promising. A different errand altogether means
different tools in stage 1, and the shape from stage 2 on holds.
