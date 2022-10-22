# QJ1520265 project (GIS part)

Source code and support files for OGC WMS and WPS developed within
QJ1520265 project, see http://rain.fsv.cvut.cz.

## Deploy Rain WPS server using Docker

### Build image

```
docker-compose build
```

### Run container

Download [BPEJ
data](https://www.spucr.cz/bpej/celostatni-databaze-bpej) from SPU
website. Place a downloaded zip file into `db/data` directory.

```
docker-compose up
```

## Quick test

### Apps

http://localhost/webapp/gisquick

http://localhost/webapp/d-rain-point

### OWS

#### WMS

GetCapabilities:

http://localhost/services/wms?service=wms&request=getcapabilities

GetMap:

http://localhost/services/wms?service=wms&request=getmap&layers=H_N2_24h&version=1.3.0&crs=EPSG:5514&bbox=-907000,-1230000,-429000,-933000&format=image/png&width=1280&height=920

#### WFS

GetCapabilities:

http://localhost/services/wfs?service=wfs&request=getcapabilities

GetFeature:

http://localhost/services/wfs?service=wfs&request=getfeature&typename=bpej&maxfeatures=10&version=2.0.0

#### WPS

GetCapabilities:

http://localhost/services/wps?service=wps&request=getcapabilities
    
DescribeProcess:

http://localhost/services/wps?service=wps&request=describeprocess&version=2.0.0&identifier=d-rain-shp
    
Execute (POST):

```
wget -q --post-file ./ows/wps/tests/request-d-rain-shp.xml 'http://localhost/services/wps?' -O -
```

Run tests:

```sh
docker-compose exec ows_tests python3 -m pytest -v -o cache_dir=/tmp/pytest_cache_dir ./tests/wps/test_wps.py
```

### Documentation

http://localhost/docs

### Notes

#### Delete pywps zombie processes

```sql
delete from pywps_requests where status=2;
```
