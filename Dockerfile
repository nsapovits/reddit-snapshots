FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cron \
    openssh-client \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update && apt-get install -y --no-install-recommends tailscale \
    && rm -rf /var/lib/apt/lists/*

COPY . /reddit-snapshots
WORKDIR /reddit-snapshots

RUN mkdir -p output/local && cp style.css output/ || true
RUN mkdir -p /etc/cron.d && printf '0 22 * * * root . /etc/environment && cd /reddit-snapshots && /usr/local/bin/python /reddit-snapshots/reddit-snapshots.py\n' > /etc/cron.d/reddit-snapshots

COPY reddit.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/reddit.sh

EXPOSE 8181
CMD ["/usr/local/bin/reddit.sh"]
