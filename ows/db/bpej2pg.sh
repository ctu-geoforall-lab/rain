#!/bin/bash -e

createdb $DBNAME
psql $DBNAME -c 'create extension postgis'

ogr2ogr -f PostgreSQL -overwrite -nln bpej -a_srs EPSG:5514 -nlt MULTIPOLYGON \
	-lco GEOMETRY_NAME=geom -lco PRECISION=NO \
        PG:dbname=$DBNAME /vsizip/data/$BPEJ_FILE

# grant privileges
echo "create user $MAPSERV_USER with encrypted password '$MAPSERV_PASSWORD';
grant select on all tables in schema public to $MAPSERV_USER;
grant select on all sequences in schema public to $MAPSERV_USER;" | psql $DBNAME

exit 0
