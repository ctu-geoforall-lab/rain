#!/bin/bash

sleep 60

while true; do
    cd /opt
    echo "Removing zombie processes older than one day"
    python remove_zombie_processes.py /data/pywps.db 1
    echo "Performing tests..."
    LOGFILE=/var/log/ows_tests/rain_ows_tests-`date -Is`.log
    RETCODE=0
    echo "============================= WPS TESTS ==============================" > $LOGFILE
    python3 -m pytest -v -o cache_dir=/tmp/pytest_cache_dir ./tests/wps/test_wps.py >> $LOGFILE
    RETCODE=$((RETCODE+$?))
    echo "============================= WMS TESTS ==============================" >> $LOGFILE
    python3 -m pytest -v -o cache_dir=/tmp/pytest_cache_dir ./tests/wms/test_wms.py >> $LOGFILE
    RETCODE=$((RETCODE+$?))
    echo "============================= WFS TESTS ==============================" >> $LOGFILE
    python3 -m pytest -v -o cache_dir=/tmp/pytest_cache_dir ./tests/wfs/test_wfs.py >> $LOGFILE
    RETCODE=$((RETCODE+$?))
    python notifier.py $RETCODE $LOGFILE
    echo "Sleeping for ${OWS_TEST_REPEAT}hrs..."
    sleep $(($OWS_TEST_REPEAT * 60 * 60))
done

exit 0
