"""The leash's lock. Claude Code calls this before every tool use in `errand run`.

--allowedTools alone is not a leash: in default mode Claude Code still lets read-only
commands (`ls`, `cat .env`) and the Read tool through without asking. This refuses
anything that is not one errand command with plain arguments. It runs as a script, not
through the package, so it has nothing to import but the standard library."""

import json
import re
import sys

# A bare word, or a quoted string. Nothing the shell would act on: no ; & | < > ( ) $ `
# or backslash outside quotes, no globs or ~, and no $ ` or backslash inside "double".
ARG = r"""(?:[^\s;&|<>()$`\\'"*?\[\]{}~]+|'[^']*'|"[^"$`\\]*")+"""
READ = "meetings|item|read|cases"


def main() -> None:
    commands = READ + ("|calendar add" if "--write" in sys.argv else "")
    allowed = re.compile(rf"errand (?:{commands})(?: +{ARG})*")
    call = json.load(sys.stdin)
    command = (call.get("tool_input") or {}).get("command", "")
    if call.get("tool_name") == "Bash" and allowed.fullmatch(command.strip()):
        return
    names = ", ".join(f"`errand {c}`" for c in commands.split("|"))
    print(f"Refused. The only commands are {names}: one per call, no pipes, && or other "
          "programs, and URLs in quotes.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
