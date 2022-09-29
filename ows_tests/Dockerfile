FROM python:3.10-slim-bullseye

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt

# set up notifier
COPY notifier.py /opt/

COPY startup.sh /opt/
RUN chmod 755 /opt/startup.sh
CMD ["/opt/startup.sh"]
