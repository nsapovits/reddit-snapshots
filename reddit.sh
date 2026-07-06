#!/usr/bin/env sh
set -eu

# Persist env vars for cron, which doesn't inherit the container's environment
{
    echo "SSH_HOST=${SSH_HOST}"
    echo "SSH_USER=${SSH_USER}"
} > /etc/environment

mkdir -p /reddit-snapshots/output

# Start tailscaled in the background, using persisted state
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
echo "[reddit.sh] tailscaled started."

# Give tailscaled a moment to initialize its socket
sleep 2

# Attempt to bring up the tailnet connection (persistent identity, reusable key)
if ! tailscale up --authkey="${TAILSCALE_AUTHKEY}" --hostname=reddit-snapshots --ssh=false; then
    echo "[reddit.sh] ERROR: tailscale up failed — auth key may be expired or invalid."
    cat > /reddit-snapshots/output/index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head><title>Reddit Snapshots - Error</title></head>
<body>
<h1>Tailscale connection failed</h1>
<p>The container could not join the tailnet, most likely because the Tailscale auth key has expired.</p>
<p>Generate a new auth key in the Tailscale admin console, update the container's environment, and restart it.</p>
</body>
</html>
HTML
    echo "[reddit.sh] Wrote error page to output/index.html. Starting HTTP server without cron."
    exec /usr/local/bin/python -m http.server 8181 -d /reddit-snapshots/output/
fi

echo "[reddit.sh] Tailscale up requested."

# Wait until Tailscale reports a healthy connection before proceeding
until tailscale status >/dev/null 2>&1; do
    echo "[reddit.sh] Waiting for Tailscale to connect..."
    sleep 2
done
echo "[reddit.sh] Tailscale connected."

# Start cron in the background
cron
echo "[reddit.sh] Cron daemon started."

# Start simple HTTP server (foreground, keeps container alive)
exec /usr/local/bin/python -m http.server 8181 -d /reddit-snapshots/output/
