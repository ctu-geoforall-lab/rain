#!/bin/bash

# WPS
envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' < /opt/pywps/pywps.cfg.template > \
         /opt/pywps/pywps.cfg
# WMS
if [ -d /opt/mapserv/wms ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' < /opt/mapserv/wms/rain.map.template > \
             /opt/mapserv/wms/rain.map
fi

# WFS
if [ -d /opt/mapserv/wfs ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT $MAPSERV_USER $MAPSERV_PASSWORD $DBNAME' \
             < /opt/mapserv/wfs/rain.map.template > \
             /opt/mapserv/wfs/rain.map
fi

# rain6h-cn-runoff
WEBAPP_DIR=/var/www/html/rain6h-cn-runoff
if [ -d $WEBAPP_DIR ] ; then
    envsubst '$NGINX_HTTP $NGINX_HOST $NGINX_PORT' \
             < $WEBAPP_DIR/main.js.template > \
             $WEBAPP_DIR/main.js
fi

# nginx
envsubst '$NGINX_HOST' < /etc/nginx/conf.d/default.conf.template > \
         /etc/nginx/conf.d/default.conf

# start nginx
spawn-fcgi -s /var/run/fcgiwrap.socket -F 5 /usr/sbin/fcgiwrap
chown www-data:www-data /var/run/fcgiwrap.socket
nginx -g 'daemon off;' &

export LD_LIBRARY_PATH=/usr/lib/grass83/lib

# create log file for MapServer otherwise it fails
touch /var/log/mapserv/mapserv.log
chmod 664 /var/log/mapserv/mapserv.log
chgrp www-data /var/log/mapserv/mapserv.log

gunicorn3 -b 0.0.0.0:8081 --workers $((2*`nproc --all`)) \
          --log-syslog  --pythonpath /opt/pywps pywps_app:application

exit 0
