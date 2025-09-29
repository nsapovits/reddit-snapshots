FROM alpine

ENV GECKODRIVER="https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache curl tar gzip ca-certificates xvfb firefox ttf-dejavu git nano python3 py3-pip
RUN python3 -m venv $VIRTUAL_ENV
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN curl -fsSL $GECKODRIVER | tar -xz -C /usr/local/bin geckodriver && chmod +x /usr/local/bin/geckodriver
RUN python3 -m pip install --no-cache-dir beautifulsoup4 selenium

COPY . /reddit-snapshots
WORKDIR /reddit-snapshots
RUN mkdir -p output/local && cp style.css output/ || true

RUN printf '0\t3\t*\t*\t*\tcd /reddit-snapshots && python /reddit-snapshots/reddit-snapshots.py\n' > /etc/crontabs/root
COPY reddit.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/reddit.sh

EXPOSE 8181
CMD ["/usr/local/bin/reddit.sh"]
