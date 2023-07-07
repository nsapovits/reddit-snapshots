FROM alpine

ENTRYPOINT "/bin/sh"

# Just be sure we start in /
WORKDIR "/"

# Enable community repository - not necessary?
#RUN cat /etc/apk/repositories | sed 's/#h/h/' | tee /etc/apk/repositories

# Start syslogd for messages
CMD ["syslogd"]

# Install dependencies
RUN apk update
RUN apk add git nano xvfb firefox dbus ttf-dejavu

# Not sure this is needed?
#RUN apk add busybox-openrc

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install dependencies
RUN pip3 install BeautifulSoup4
RUN pip3 install selenium

# Clone repository
RUN git clone https://github.com/nsapovits/reddit-snapshots.git
WORKDIR "/reddit-snapshots"
RUN chmod +x cron.sh

# Prep for Firefox to run
#RUN rc-update add local default
#RUN echo "#!/bin/sh" | tee /etc/local.d/Xvfb.start
#RUN echo "/usr/bin/Xvfb :99 -ac &" | tee -a /etc/local.d/Xvfb.start
#RUN chmod +x /etc/local.d/Xvfb.start
CMD ["/usr/bin/Xvfb", ":99", "-ac", "&"]

# Prep for script execution
RUN mkdir output
RUN mkdir output/local
RUN cp style.css output/

# Execute script (first-run)
#RUN python3 reddit-snapshots.py

# Start Python HTTP server
WORKDIR "/reddit-snapshots/output"
#CMD ["python3", "-m", "http.server", "8181", "&"]

# Set up cron job to run script daily
#RUN rc-service crond start && rc-update add crond
RUN echo -e '35\t3\t*\t*\t*\tsh /reddit-snapshots/cron.sh' | tee -a /etc/crontabs/root
CMD ["crond"]
#RUN rc-service crond restart

# Entrypoint
#ENTRYPOINT ["crond", "-f"] -- probably put the python http server here instead?

CMD ["/usr/bin/python3", "-m", "http.server", "8181", "-d", "/reddit-snapshots/output/"]



# Expose 8181 for Python HTTP server
EXPOSE 8181