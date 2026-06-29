#!/usr/bin/env sh
set -eu

# Start cron in the background (log level 8 for debugging)
crond -l 8

# Optional: log something so you know cron started
echo "[reddit.sh] Cron daemon started."

# Start simple HTTP server (foreground, keeps container alive)
exec /usr/local/bin/python -m http.server 8181 -d /reddit-snapshots/output/
