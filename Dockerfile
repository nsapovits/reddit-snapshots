FROM alpine

# Just be sure we start in /
WORKDIR "/"

# Start cron for daily script execution
RUN echo 'crond' | tee run.sh

# Start the X virtual frame buffer for Firefox
RUN echo '/usr/bin/Xvfb :99 -ac &' | tee -a run.sh

# Start the Python HTTP server to host the output files
RUN echo 'python3 -m http.server 8181 -d /reddit-snapshots/output/' | tee -a run.sh

# Set the script as executable
RUN chmod +x run.sh

# Install dependencies
RUN apk update
RUN apk add git nano xvfb firefox ttf-dejavu

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install Python packages
RUN pip3 install BeautifulSoup4
RUN pip3 install selenium

# Clone repository
# Can probably do this better with COPY or ADD commands instead
RUN git clone https://github.com/nsapovits/reddit-snapshots.git
WORKDIR "/reddit-snapshots"
RUN chmod +x cron.sh

# Prep for script execution
RUN mkdir output
RUN mkdir output/local
RUN cp style.css output/

# Execute script (first-run)
#RUN python3 reddit-snapshots.py

# Set up cron job to run script daily
RUN echo -e '30\t3\t*\t*\t*\tsh /usr/bin/python3 /reddit-snapshots/reddit-snapshots.py' | tee -a /etc/crontabs/root

# Use the run.sh file we created earlier to start cron, the Xvfb, and the Python HTTP server
CMD ["/bin/sh", "-c", "/run.sh"]

# Expose 8181 for Python HTTP server
EXPOSE 8181