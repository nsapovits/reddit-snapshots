FROM alpine

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install dependencies
RUN pip3 install BeautifulSoup4
RUN pip3 install selenium

# Install git
RUN apk add git


# Expose 8181 for Python HTTP server
EXPOSE 8181