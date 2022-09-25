# FROM mundialis/grass-py3-pdal:stable-ubuntu
FROM ubuntu:18.04

# install requirements
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install --yes software-properties-common gettext-base
RUN add-apt-repository --yes ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update
RUN apt-get install --yes python3-pip python3-pyproj gunicorn3 nginx
RUN apt-get install --yes grass-core grass-doc grass-dev
RUN apt-get install --yes cgi-mapserver fcgiwrap
RUN python3 -m pip install -r /tmp/requirements.txt

# set up pyWPS
RUN mkdir -p /var/www/wps/output
RUN mkdir -p /var/log/pypws
RUN rm /etc/nginx/sites-enabled/default

# install GRASS extensions
RUN grass --tmp-location EPSG:5514 --exec g.extension -s r.subdayprecip.design

# patch pyWPS 4.2.8
COPY wps/pywps/patches/ /tmp/
RUN patch -p0 < /tmp/Service.diff
RUN patch -p0 < /tmp/Process.diff

# set up MapServer
RUN mkdir -p /opt/mapserv/
RUN mkdir -p /var/log/mapserv/

# run Gunicorn
COPY startup.sh /opt/startup.sh
CMD ["/opt/startup.sh"]
