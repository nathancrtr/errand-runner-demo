#!/bin/sh
# Install (or reinstall) the Friday 07:45 job. launchd runs a missed job on wake,
# so a laptop that was asleep just runs it later in the day.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL=com.nathancarter.errand-council
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$REPO/data" "$HOME/Library/LaunchAgents"
sed -e "s|__REPO__|$REPO|g" -e "s|__HOME__|$HOME|g" "$REPO/launchd/$LABEL.plist" > "$PLIST"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl print "gui/$(id -u)/$LABEL" | head -3
echo "installed; run it now with: launchctl kickstart -k gui/$(id -u)/$LABEL"
