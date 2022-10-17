# -*- coding: utf-8 -*-

####################################################################
# QJ1520265 project - source code and support files for OGC WMS and
# WPS implementation http://rain.fsv.cvut.cz
#
# Purpose: WPS processes (CSV)
# Author: Martin Landa <martin.landa fsv.cvut.cz>
# Licence: see LICENCE file for details
####################################################################

import os
import sys
from subprocess import PIPE

from . import SubDayPrecipProcess
from grass.pygrass.modules import Module

class SubDayPrecipCsv(SubDayPrecipProcess):
     def __init__(self):
          super(SubDayPrecipCsv, self).__init__(
               identifier="d-rain-csv",
               description=u"Vraci vycislene navrhove srazky jako atributova data ve formatu CSV.",
               input_params=['input', 'keycolumn', 'return_period', 'rainlength', 'area_size'],
               output_params=['output_csv']
          )
          
     def export(self):
          self.output_file = '{}/{}.csv'.format(self.output_dir, self.map_name)

          cols = [self.keycolumn]
          for rp in self.return_period:
               cols.append('H_{}T{}'.format(rp, self.rainlength))

          data = Module('v.db.select',
                        map=self.map_name,
                        separator='comma',
                        flags='c',
                        columns=cols,
                        stdout_=PIPE)

          sep = ','
          with open(self.output_file, 'w') as fd:
               fd.write(sep.join(
                    map(lambda x: x + '_mm' if x.startswith('H_') else x, cols)
               ))
               fd.write(os.linesep)
               for line in data.outputs.stdout.splitlines():
                    idx = 0
                    for val in line.split(','):
                         if idx == 0:
                              fd.write('{}'.format(val))
                         else:
                              fd.write('{0}{1:.1f}'.format(sep, float(val)))
                         idx += 1
                    fd.write(os.linesep)

          return self.output_file
