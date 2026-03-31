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
from subprocess import PIPE

from . import SubDayPrecipProcess
from grass.pygrass.modules import Module

class DRainPoint(SubDayPrecipProcess):
     def __init__(self):
          SubDayPrecipProcess.__init__(
               self,
               identifier="d-rain-point",
               title="Nastroj vraci vycislenou navrhovou srazku pro zvoleny bod ve WGS-84.",
               input_params=['obs', 'return_period', 'rainlength'],
               output_params=['output_value'],
               version=1.0
          )

          self.mapset = 'rain6h'
          
          os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
          os.environ['HOME'] = '/tmp' # needed by G_home()

     def compute_subdayprecip_design(self, rainlength):
          rasters = ['H_{}T{}@rain6h'.format(r, rainlength) for r in self.return_period]
          Module('r.subdayprecip.design',
                 map=self.map_name, return_period=rasters,
                 rainlength=rainlength)

          columns = ['H_{}T{}'.format(r, rainlength) for r in self.return_period]
          p = Module('v.db.select', map=self.map_name, flags='c',
                     columns=columns,
                     stdout_=PIPE)

          self._result = []
          for v in p.outputs.stdout.rstrip().split('|'):
               if len(v) == 0:
                    raise Exception("Bod '{0},{1}' nelezi na uzemi CR".format(
                         request.inputs['obs_x'][0].data,
                         request.inputs['obs_y'][0].data
                    ))
               self._result.append(float(v))

     def export(self):
          return '{}'.format(
               ','.join('%.1f' % v for v in self._result)
          )
          
