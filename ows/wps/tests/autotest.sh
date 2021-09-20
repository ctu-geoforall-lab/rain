#!/bin/sh -e

# Test WPS processes
#URL="http://localhost"
URL="https://rain1.fsv.cvut.cz"
DATA="@xlink:href=http://rain.fsv.cvut.cz/geodata/test.gml"
KEY="HLGP_ID"
RP="N2,N5,N100"
RL="360"
COL="HLGP_ID"
STYP="E,F"
VALUE="25"
LIMIT="10000"

cp ows/wps/tests/request-d-rain-shp.xml ows/wps/tests/request-soil-texture-hsg.xml /tmp
cd /tmp

echo "**************************************************************"
echo "* d-rain-shp (POST) "
echo "**************************************************************"

wget -q --post-file request-d-rain-shp.xml "${URL}/services/wps?" -O response.xml
file=`cat response.xml | grep '\<wps:Reference' | cut -d'"' -f2`
wget -q $file
echo "RESULT:"
ogrinfo -ro -so /vsizip/`basename $file` subdayprecip_output | grep 'H_N'

echo "**************************************************************"
echo "* d-rain-shp (GET|XLINK)"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=d-rain-shp&datainputs=input=${DATA};return_period=${RP};rainlength=${RL};area_size=${LIMIT}"
echo $CURL
file=`curl "$CURL" |  grep '\<wps:Reference' | cut -d'"' -f2`

wget -q $file
echo "RESULT:"
ogrinfo -ro -so /vsizip/`basename $file` subdayprecip_output | grep 'H_N'

echo "**************************************************************"
echo "* d-rain-csv"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=d-rain-csv&datainputs=input=${DATA};return_period=${RP};rainlength=${RL};keycolumn=$COL;area_size=${LIMIT}"
echo $CURL
file=`curl "$CURL" | grep '\<wps:Reference' | cut -d'"' -f2`

wget -q $file
echo "RESULT:"
cat `basename $file`

echo "**************************************************************"
echo "* d-rain-point"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=d-rain-point&datainputs=obs_x=15.11784;obs_y=49.88598;return_period=${RP};rainlength=${RL}"
echo $CURL
value=`curl $CURL | grep "\<wps:LiteralData" | cut -d'>' -f 2 | cut -d'<' -f 1`

echo "RESULT:"
echo $value

echo "**************************************************************"
echo "* d-rain6h-timedist (reduction enabled)"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=d-rain6h-timedist&datainputs=input=${DATA};return_period=${RP};keycolumn=${COL};type=${STYP}"
echo $CURL
file=`curl $CURL | grep '\<wps:Reference' | cut -d'"' -f2`
wget -q $file
echo "RESULT:"
cat `basename $file` | head -n2

echo "**************************************************************"
echo "* d-rain6h-timedist (reduction disabled)"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=d-rain6h-timedist&datainputs=input=${DATA};return_period=${RP};keycolumn=${COL};type=${STYP};area_red=false"
echo $CURL
file=`curl $CURL | grep '\<wps:Reference' | cut -d'"' -f2`
wget -q $file
echo "RESULT:"
cat `basename $file` | head -n2

echo "**************************************************************"
echo "* raintotal6h-timedist"
echo "**************************************************************"

CURL="${URL}/services/wps?service=wps&version=1.0.0&request=Execute&identifier=raintotal6h-timedist&datainputs=value=${VALUE};type=${STYP}"
echo $CURL
file=`curl $CURL | grep '\<wps:Reference' | cut -d'"' -f2`
wget -q $file
echo "RESULT:"
cat `basename $file` | head -n2

echo "**************************************************************"
echo "* soil-texture-hsg"
echo "**************************************************************"
wget -q --post-file request-soil-texture-hsg.xml "${URL}/services/wps?" -O response.xml
file=`cat response.xml | grep '\<wps:Reference' | cut -d'"' -f2`
wget -q $file
echo "RESULT:"
unzip -l `basename $file` | grep '.tif$'

exit 0
