FROM python:3.10-slim-bullseye

# install system libraries
RUN apt-get update
RUN apt-get install -y libgdal-dev python3-pip git wget

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U setuptools==57.5.0 # error in GDAL setup command: use_2to3 is invalid.
RUN python3 -m pip install -r /tmp/requirements.txt

WORKDIR /opt

# set up notifier
RUN mkdir /var/log/ows_tests
COPY remove_zombie_processes.py notifier.py /opt/

COPY startup.sh /opt/
RUN chmod 755 /opt/startup.sh
CMD ["/opt/startup.sh"]
