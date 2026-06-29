FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache ca-certificates
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel requests

COPY . /reddit-snapshots
WORKDIR /reddit-snapshots

RUN mkdir -p output/local && cp style.css output/ || true
RUN printf '0 22 * * * cd /reddit-snapshots && /usr/local/bin/python /reddit-snapshots/reddit-snapshots.py\n' > /etc/crontabs/root

COPY reddit.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/reddit.sh

EXPOSE 8181
CMD ["/usr/local/bin/reddit.sh"]
