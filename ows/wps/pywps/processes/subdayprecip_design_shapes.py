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

class SubDayPrecipShapesBase(object):
     def __init__(self):
          self.mapset = 'rl360_v2'
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

class SubDayPrecipShapes(SubDayPrecipShapesBase, SubDayPrecipProcess):
     def __init__(self):
          SubDayPrecipProcess.__init__(self,
               identifier="d-rain6h-timedist",
               description=u"Vraci tvary navrhovych srazek v tabulkove forme s pevne stanovenou delkou srazky 6 hodin.",
               input_params=['input', 'keycolumn', 'return_period', 'type', 'area_red'],
               output_params=['output_shapes', 'output_probabilities']
          )
          SubDayPrecipShapesBase.__init__(self)

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
          nl = '\r\n'
          # write header
          fd.write('{key}{sep}CAS_min'.format(key=self.keycolumn, sep=self.sep))
          for rp in self.return_period:
               for stype in self.shapetype:
                    fd.write('{sep}H_{rast}typ{stype}_mm'.format(
                              sep=self.sep, stype=stype, rast=rp)
                    )
          fd.write(nl)

          # process features
          self.report_progress(25, f"Exporting shapes")
          for fid, attrib in data['values'].items():
               LOGGER.debug('FID={}: {}'.format(attrib[0], attrib[1:]))
               valid = True if float(attrib[1]) > 0 else False
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
                    fd.write('{seps}'.format(
                         seps=self.sep * len(attrib[1:] * len(self.shapetype)))
                    )
                    fd.write(nl)

     def export_probabilities(self, fd, data):
          nl = '\r\n'
          # write header
          fd.write('{key}'.format(key=self.keycolumn))
          # H columns
          for col in data['columns'][1:]: # skip key column
               fd.write('{sep}{col}_mm'.format(sep=self.sep, col=col))
          # P columns
          for rp in self.return_period:
               for stype in self.shapetype:
                    fd.write('{sep}P_{rast}typ{stype}_%'.format(
                         sep=self.sep, stype=stype, rast=rp)
                    )
          # QAPI columns
          for stype in self.shapetype:
               fd.write('{sep}QAPI_typ{stype}_%'.format(
                    sep=self.sep, stype=stype)
               )
          fd.write(nl)

          # compute timeshape percentage
          data_perc = self._compute_timeshapes_perc()

          # process features
          self.report_progress(90, f"Exporting probabilities")
          for fid, attrib in data['values'].items():
               LOGGER.debug('FID={}: {}'.format(attrib[0], attrib[1:]))
               valid = True if float(attrib[1]) > 0 else False
               fd.write('{fid}'.format(
                    fid=attrib[0]
               ))
               for val in data['values'][fid][1:]: # skip key column
                    fd.write('{sep}{val:.1f}'.format(sep=self.sep, val=float(val)))
               for val in data_perc['values'][fid]:
                    if valid:
                         val = float(val)
                    else:
                         val = -1
                    fd.write('{sep}{val:.1f}'.format(
                         sep=self.sep, val=val
                    ))
               # for stype in self.shapetype:
               #      fd.write('{sep}-1'.format(sep=self.sep))
               fd.write(nl)

if __name__ == "__main__":
     process = Process()
     process.execute()
