FROM postgis/postgis:15-3.3

ADD conf.sql /docker-entrypoint-initdb.d/97_conf.sql
ADD epsg5514.sql /docker-entrypoint-initdb.d/98_epsg5514.sql
ADD bpej2pg.sh /docker-entrypoint-initdb.d/99_bpej2pg.sh

RUN apt-get update && apt-get install --yes wget gdal-bin
