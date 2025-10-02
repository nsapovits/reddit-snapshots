docker run -d \
  --name reddit-snapshots \
  --restart unless-stopped \
  --memory 1G \
  -p 8181:8181 \
  -v /etc/localtime:/etc/localtime:ro \
  reddit-snapshots
