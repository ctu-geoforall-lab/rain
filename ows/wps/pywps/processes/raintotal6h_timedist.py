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
from .d_rain6h_timedist import DRain6hTimedistBase

import grass.script as gscript # TODO: replace by pyGRASS

class Raintotal6hTimedist(DRain6hTimedistBase, SubDayPrecipProcess):
     def __init__(self):
          SubDayPrecipProcess.__init__(self,
               identifier="raintotal6h-timedist",
               title="Nástroj raintotal6h-timedist je doplňkovým nástrojem, který vychází z předchozí varianty d-rain-timedist.",
               abstract="Nástroj raintotal6h-timedist je doplňkovým nástrojem, který vychází z předchozí varianty d-rain-timedist. Návrhová 6hodinová srážka není odvozována pro žádnou konkrétní lokalitu ani dobu opakování, nástroj pouze rozloží uživatelem zadaný 6hodinový úhrn do zvolených variant ze šesti typizovaných průběhů intenzit A–F, bez bližší specifikace pravděpodobnosti jejich výskytu (ta je vázána vždy ke konkrétní lokalitě a době opakování).",
               input_params=['value', 'shape'],
               output_params=['output_shapes'],
               version=3.0
          )
          DRain6hTimedistBase.__init__(self)

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
               fd.write(f'{self.sep}H_tvar{stype}_mm')
          fd.write(self.nl)

          # process features
          for s in shapes:
               time = s[0]
               timeshapes = s[1:]
               fd.write(f'{time}')
               for shape in timeshapes:
                    val = (float(self.value) * float(shape)) / 100
                    fd.write(f'{self.sep}{val:.1f}')
               fd.write(self.nl)

if __name__ == "__main__":
     process = Process()
     process.execute()
