#!/usr/bin/env sh
set -eu

# Start cron (background, logs to stdout)
crond -l 8

# Start X virtual framebuffer for Firefox
/usr/bin/Xvfb :99 -ac &

# Simple HTTP server hosting output dir (foreground)
exec /opt/venv/bin/python -m http.server 8181 -d /reddit-snapshots/output/
