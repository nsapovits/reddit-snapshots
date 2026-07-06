docker run -d \
  --name reddit-snapshots \
  --restart unless-stopped \
  --memory 1G \
  -p 8181:8181 \
  --env-file .env \
  --cap-add=NET_ADMIN \
  --device=/dev/net/tun \
  -v /etc/localtime:/etc/localtime:ro \
  -v ~/reddit-snapshots-data/ssh/reddit-snapshots-key:/root/.ssh/id_ed25519:ro \
  -v ~/reddit-snapshots-data/tailscale-state:/var/lib/tailscale \
  reddit-snapshots
