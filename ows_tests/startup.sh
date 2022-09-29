#!/bin/bash

sleep 10
while true; do
    cd /opt/tests
    echo "Performing tests..."
    LOGFILE=/var/log/rain_ows_tests-`date -Is`.log
    RETCODE=0
    echo "============================= WPS TESTS ==============================" > $LOGFILE
    python3 -m pytest -x -v -s -o cache_dir=/tmp/pytest_cache_dir wps/test_wps.py >> $LOGFILE
    RETCODE=$((RETCODE+$?))
    python notifier.py $RETCODE $LOGFILE
    echo "Sleeping for ${OWS_TEST_REPEAT}hrs..."
    sleep $(($OWS_TEST_REPEAT * 60 * 60))
done

exit 0
