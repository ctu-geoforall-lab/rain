# -*- coding: utf-8 -*-

####################################################################
# QJ1520265 project - source code and support files for OGC WMS and
# WPS implementation http://rain.fsv.cvut.cz
#
# Purpose: WPS processes (Shapefile)
# Author: Martin Landa <martin.landa fsv.cvut.cz>
# Licence: see LICENCE file for details
####################################################################

import os
import sys
import types
import time
from zipfile import ZipFile

from . import SubDayPrecipProcess, LOGGER
import grass.script as gscript # TODO: replace by pyGRASS

class DRain6hTimedistBase(object):
     def __init__(self):
          self.mapset = 'rain6h'
          self.sep = ','
          self.rainlength = '360'

     def query_shapes(self):
          sql = 'select min'
          for stype in self.shapetype:
               sql += ',typ{}'.format(stype)
          sql += ' from tvary'
          gisenv = gscript.gisenv()

          return gscript.db_select(sql=sql, driver='sqlite',
                                   database=os.path.join(
                                        gisenv['GISDBASE'], gisenv['LOCATION_NAME'],
                                        self.mapset, 'sqlite/sqlite.db')
          )

class DRain6hTimedist(DRain6hTimedistBase, SubDayPrecipProcess):
     def __init__(self):
          SubDayPrecipProcess.__init__(self,
               identifier="d-rain6h-timedist",
               # title="Nástroj d-rain6h-timedist vrací šest variant průběhu pětiminutových intenzit 6hodinových návrhových srážek zvolené doby opakování, včetně pravděpodobnosti výskytu daného průběhu v zadané lokalitě.",
               # abstract="Nástroj d-rain6h-timedist vrací šest variant průběhu pětiminutových intenzit 6hodinových návrhových srážek zvolené doby opakování, včetně pravděpodobnosti výskytu daného průběhu v zadané lokalitě (definované jako bod nebo polygon). Celkový úhrn všech šesti variant průběhů je vždy stejný a je odvozen regionální frekvenční analýzou šestihodinových maximálních úhrnů z 10leté řady radarových odrazivostí a delších, dostupných řad staničních měření (viz Datové podklady). Při výpočtu je kontrolováno, zda plocha území přesáhla plochu 20 km2 a v kladném případě nástroj provádí redukci celkového úhrnu. Výstup nástroje je ve formátu CSV a jeho struktura je totožná s výstupem webové mapové aplikace na platformě Gisquick, která tento nástroj používá k vyčíslení návrhové srážky na pevně definovaných povodích IV. řádu.",
               title="Nastroj d-rain6h-timedist vraci sest variant prubehu petiminutovych intenzit 6hodinovych navrhovych srazek zvolene doby opakovani, vcetne pravdepodobnosti vyskytu daneho prubehu v zadane lokalite.",
               abstract="Nastroj d-rain6h-timedist vraci sest variant prubehu petiminutovych intenzit 6hodinovych navrhovych srazek zvolene doby opakovani, vcetne pravdepodobnosti vyskytu daneho prubehu v zadane lokalite (definovane jako bod nebo polygon). Celkovy uhrn vsech sesti variant prubehu je vzdy stejny a je odvozen regionalni frekvencni analyzou sestihodinovych maximalnich uhrnu z 10lete rady radarovych odrazivosti a delsich, dostupnych rad stanicnich mereni (viz Datove podklady). Pri vypoctu je kontrolovano, zda plocha uzemi presahla plochu 20 km2 a v kladnem pripade nastroj provadi redukci celkoveho uhrnu. Vystup nastroje je ve formatu CSV a jeho struktura je totozna s vystupem webove mapove aplikace na platforme Gisquick, ktera tento nastroj pouziva k vycisleni navrhove srazky na pevne definovanych povodich IV. radu.",
               input_params=['input', 'keycolumn', 'return_period', 'shape', 'area_red'],
               output_params=['output_shapes', 'output_probabilities'],
               version=3.0
          )
          DRain6hTimedistBase.__init__(self)

     def _compute_timeshapes_perc(self):
          # filename syntax: sjtsk_zastoupeni_shluku_cA_100yr_perc
          columns = []
          i = 1
          count = len(self.return_period)
          for rp in self.return_period:
               self.report_progress(25 + (i * 65/count), f"Computing timeshapes for {rp}")
               for stype in self.shapetype:
                    n = rp.lstrip('N')
                    columns.append('c{types}_{n}yr_perc'.format(
                         types=stype, n=n
                    ))
                    rast_name = '{types}_{n:03d}@{ms}'.format(
                         types=stype, n=int(n), ms=self.mapset
                    )
                    self.v_rast_stats(rast_name, columns[-1])
               i += 1

          # QAPI
          for stype in self.shapetype:
               columns.append('qapi_{types}_perc'.format(
                    types=stype, n=n
               ))
               rast_name = 'a06_t{types}z_1@{ms}'.format(
                    types=stype, ms=self.mapset
               )
               self.v_rast_stats(rast_name, columns[-1])

          return gscript.vector_db_select(
               map=self.map_name,
               columns=','.join(map(lambda x: '{}_average'.format(x), columns))
          )

     def export(self):
          LOGGER.debug("Shapes computation started")
          start = time.time()

          # query map attributes
          columns = list(map(lambda x: 'H_{}T{}'.format(x, self.rainlength), self.return_period))
          columns.insert(0, self.keycolumn)
          data = gscript.vector_db_select(map=self.map_name, columns=','.join(columns))

          # export csv
          self.output_shapes = '{}/{}-shapes.csv'.format(self.output_dir, self.identifier)
          with open(self.output_shapes, 'w') as fd:
               self.export_shapes(fd, self.query_shapes(), data)

          self.output_probabilities = '{}/{}.csv'.format(
               self.output_dir, self.identifier)
          with open(self.output_probabilities, 'w') as fd:
               self.export_probabilities(fd, data)

          LOGGER.info("Shapes calculated successfully: {} sec".format(time.time() - start))

          return self.output_shapes, self.output_probabilities

     def export_shapes(self, fd, shapes, data):
          # write header
          fd.write('{key}{sep}CAS_min'.format(key=self.keycolumn, sep=self.sep))
          for rp in self.return_period:
               for stype in self.shapetype:
                    fd.write('{sep}H_{rast}tvar{stype}_mm'.format(
                              sep=self.sep, stype=stype, rast=rp)
                    )
          fd.write(self.nl)

          # process features
          self.report_progress(25, f"Exporting shapes")
          for fid, attrib in data['values'].items():
               LOGGER.debug('FID={}: {}'.format(attrib[0], attrib[1:]))
               valid = True if float(attrib[1]) > 0 else False
               fd.write('{fid}{sep}0{sep}{zeros}{nl}'.format(
                    fid=attrib[0], sep=self.sep, nl=self.nl,
                    zeros=self.sep.join(['0.000'] * len(self.return_period) * len(self.shapetype))))
               for s in shapes:
                    time = s[0]
                    timeshapes = s[1:]
                    fd.write('{fid}{sep}{time}'.format(fid=attrib[0], time=time, sep=self.sep))
                    for val in attrib[1:]:
                         val = float(val)
                         for shape in timeshapes:
                              if valid:
                                   val_type = val * float(shape) / 100.0
                              fd.write('{sep}{val:.3f}'.format(
                                   sep=self.sep,
                                   val=val_type
                              ))
                    fd.write(self.nl)

     def export_probabilities(self, fd, data):
          # write header
          fd.write(f'{self.keycolumn}')
          # H columns
          for col in data['columns'][1:]: # skip key column
               fd.write(f'{self.sep}{col}_mm')
          # P columns
          for rp in self.return_period:
               for stype in self.shapetype:
                    fd.write(f'{self.sep}P_{rp}tvar{stype}_%')
          # QAPI columns
          for stype in self.shapetype:
               fd.write(f'{self.sep}QAPI_tvar{stype}')
          fd.write(self.nl)

          # compute timeshape percentage
          data_perc = self._compute_timeshapes_perc()

          # process features
          self.report_progress(90, "Exporting probabilities")
          for fid, attrib in data['values'].items():
               prec=1
               LOGGER.debug(f'FID={attrib[0]}: {attrib[1]}')
               valid = True if float(attrib[1]) > 0 else False
               fd.write(f'{attrib[0]}')
               for val in data['values'][fid][1:]: # skip key column
                    fd.write(f'{self.sep}{float(val):.{prec}f}')
               i = 1
               for val in data_perc['values'][fid]:
                    if i == len(self.return_period) * len(self.shapetype):
                         prec=2
                    if valid:
                         val = float(val)
                    else:
                         val = -1
                    fd.write(f'{self.sep}{val:.{prec}f}')
                    i += 1
               fd.write(self.nl)

if __name__ == "__main__":
     process = Process()
     process.execute()
