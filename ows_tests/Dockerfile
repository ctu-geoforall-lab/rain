FROM python:3.12-slim-bookworm

# install system libraries
RUN apt-get update
RUN apt-get install -y libgdal-dev git wget g++

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt

WORKDIR /opt

# set up notifier
RUN mkdir /var/log/ows_tests
COPY remove_zombie_processes.py notifier.py /opt/

COPY startup.sh /opt/
RUN chmod 755 /opt/startup.sh
CMD ["/opt/startup.sh"]
