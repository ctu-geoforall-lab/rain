#!/bin/bash

# WPS
envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' < /opt/pywps/pywps.cfg.template > \
         /opt/pywps/pywps.cfg
# WMS
if [ -d /opt/mapserv/wms ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' < /opt/mapserv/wms/subdayprecip.map.template > \
             /opt/mapserv/wms/subdayprecip.map
fi

# WFS
if [ -d /opt/mapserv/wfs ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT $MAPSERV_USER $MAPSERV_PASSWORD $DBNAME' \
             < /opt/mapserv/wfs/subdayprecip.map.template > \
             /opt/mapserv/wfs/subdayprecip.map
fi

# d-rain-point
if [ -d /var/www/html/d-rain-point ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' \
             < /var/www/html/d-rain-point/main.js.template > \
             /var/www/html/d-rain-point/main.js
fi

# nginx
envsubst '$NGINX_HOST' < /etc/nginx/conf.d/default.conf.template > \
         /etc/nginx/conf.d/default.conf

# start nginx
/etc/init.d/fcgiwrap start && nginx -g 'daemon off;' &

export LD_LIBRARY_PATH=/usr/lib/grass78/lib

# create log file for MapServer otherwise it fails
touch /var/log/mapserv/mapserv.log
chmod 664 /var/log/mapserv/mapserv.log
chgrp www-data /var/log/mapserv/mapserv.log

gunicorn3 -b 0.0.0.0:8081 --workers $((2*`nproc --all`)) \
          --log-syslog  --pythonpath /opt/pywps pywps_app:application

exit 0
