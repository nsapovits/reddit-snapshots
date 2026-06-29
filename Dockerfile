FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates cron && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel playwright
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . /reddit-snapshots
WORKDIR /reddit-snapshots

RUN mkdir -p output/local && cp style.css output/ || true
RUN mkdir -p /etc/cron.d && printf '0 22 * * * root cd /reddit-snapshots && /usr/local/bin/python /reddit-snapshots/reddit-snapshots.py\n' > /etc/cron.d/reddit-snapshots

COPY reddit.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/reddit.sh

EXPOSE 8181
CMD ["/usr/local/bin/reddit.sh"]
