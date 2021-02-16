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
from .subdayprecip_design_shapes import SubDayPrecipShapesBase

import grass.script as gscript # TODO: replace by pyGRASS

class SubDayPrecipShapesTotal(SubDayPrecipShapesBase, SubDayPrecipProcess):
     def __init__(self):
          SubDayPrecipProcess.__init__(self,
               identifier="raintotal6h-timedist",
               description=u"Vraci tvary uzivatelem zadane hodnoty srazky v tabulkove forme s pevne stanovenou delkou srazky 6 hodin.",
               input_params=['value', 'type'],
               output_params=['output_shapes']
          )
          SubDayPrecipShapesBase.__init__(self)

     def export(self):
          LOGGER.debug("Shapes computation started")
          start = time.time()

          # export csv
          self.output_file = '{}/{}.csv'.format(self.output_dir, self.identifier)
          with open(self.output_file, 'w') as fd:
               self.export_csv(fd, self.query_shapes(), data=None)

          LOGGER.info("Shapes calculated successfully: {} sec".format(time.time() - start))

          return self.output_file

     def export_csv(self, fd, shapes, data=None):
          # write header
          fd.write('CAS_min')
          for stype in self.shapetype:
               fd.write('{sep}H_typ{stype}_mm'.format(
                    sep=self.sep, stype=stype)
               )
          fd.write('\r\n')

          # process features
          for s in shapes:
               time = s[0]
               timeshapes = s[1:]
               fd.write('{time}'.format(time=time, sep=self.sep))
               for shape in timeshapes:
                    fd.write('{sep}{val:.3f}'.format(sep=self.sep,
                                                 val=(float(self.value)*float(shape))/100)
                    )
               fd.write('\r\n')

if __name__ == "__main__":
     process = Process()
     process.execute()
