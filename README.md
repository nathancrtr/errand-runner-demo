# errand-runner-demo

One repeated check, turned into something that runs on its own. This time a model
does the reading, every Friday, with a short list of tools and a paragraph of taste.

Start with [ERRAND.md](ERRAND.md). Everything else here exists to make that
sentence true.

## What it does

1. **Meetings.** `errand meetings` lists what the City Council and the county board
   will take up in the next two weeks, every agenda item with its attachments. Raleigh
   publishes to eSCRIBE, Wake County to Legistar. Both are public; no keys anywhere.
2. **Read.** `errand read <url>` turns an attachment or page (PDF, docx, HTML) into
   text. `errand item` shows one agenda item in full.
3. **Cases.** `errand cases` lists rezoning cases in process within `radius_km` of
   home, from the city's open-data layer, with the distance computed here.
4. **Run.** `errand run` hands those tools to a model, with [ERRAND.md](ERRAND.md) as
   the job and [PROFILE.md](PROFILE.md) as the taste. It decides what to open, writes a
   digest to `data/last-digest.md`, and leaves a trace of what it opened in
   `data/last-trace.txt`. The tool count is not known until it runs.
5. **Calendar.** The one writer. `errand calendar add` appends an event to
   `data/council.ics` keyed by UID, so a second run changes nothing. The model may
   add; there is no tool to remove or edit.
6. **Every Friday.** A launchd job at 07:45.

## Setup

```sh
uv venv && uv pip install -e .
cp .env.example .env                # your home coordinates, from any map app
.venv/bin/errand meetings | head    # live agendas
.venv/bin/errand cases
.venv/bin/errand run --dry-run      # the model reads; the calendar is untouched
.venv/bin/errand run                # the same, and it may add to data/council.ics
scripts/install-launchd.sh
```

`errand run` needs the `claude` CLI. Every download is cached under `data/cache/` for
three days, so a second run works offline. `open data/council.ics` imports the events
into Calendar.app.

## The leash

`errand run` is a nested Claude Code started with `--permission-mode default` and an
allowed-tools list of four command prefixes, five when the writer is on. In rehearsal it
was asked to `touch` a file and was blocked, and `errand cases; touch x` was blocked as
a whole. Harmless glue like `echo` and `| head` passes. The policy is prose in
[errand/run.py](errand/run.py); the taste is prose in PROFILE.md; the writer is one
command that only appends. All three are readable by someone who does not write code.

## Changing the errand

- A different neighborhood: two lines in `.env` and a paragraph in `PROFILE.md`.
- A different city: one block in `watch.toml`, if it publishes to Legistar or eSCRIBE.
  Hundreds of cities do.
- A different errand altogether: replace the tools in `errand/`. `run.py` only needs
  commands a model can call and a paragraph saying what matters.

[demo/RUNBOOK.md](demo/RUNBOOK.md) is the script for building this live in 25
minutes, with tags `stage-0` through `stage-3` as the safety net.
