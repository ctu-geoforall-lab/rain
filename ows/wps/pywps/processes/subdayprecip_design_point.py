# -*- coding: utf-8 -*-

####################################################################
# QJ1520265 project - source code and support files for OGC WMS and
# WPS implementation http://rain.fsv.cvut.cz
#
# Purpose: WPS processes (Shapefile)
# Author: Martin Landa <martin.landa fsv.cvut.cz>
# Licence: see LICENCE file for details
####################################################################

import sys
from subprocess import PIPE

from . import SubDayPrecipProcess, LOGGER
from grass.pygrass.modules import Module

class SubDayPrecipPoint(SubDayPrecipProcess):
     def __init__(self):

          super(SubDayPrecipPoint, self).__init__(
               identifier="d-rain-point",
               description=u"Vraci vycislenou navrhovou srazku pro zvoleny bod ve WGS-84.",
               input_params=['obs', 'return_period', 'rainlength'],
               output_params=['output_value']
          )

     def _handler(self, request, response):
          self.rasters= [rp.data.strip() for rp in request.inputs['return_period']]
          self.rainlength = request.inputs['rainlength'][0].data

          Module('g.region', raster=self.rasters[0])

          map_name = 'obs'
          p = Module('m.proj',
                     coordinates=[request.inputs['obs_x'][0].data,
                                  request.inputs['obs_y'][0].data],
                     proj_in='+init=epsg:4326', proj_out='+init=epsg:5514', stdout_=PIPE)
          x, y, z = p.outputs.stdout.split('|')
          vector_input="1|{}|{}".format(x, y)
          LOGGER.debug('Input: {}'.format(vector_input))
          Module('v.in.ascii', input='-', output=map_name,
                 cat=1, x=2, y=3, stdin_=vector_input)
          Module('v.db.addtable', map=map_name)
          LOGGER.debug("Subday computation started")
          Module('r.subdayprecip.design',
                 map=map_name, return_period=self.rasters,
                 rainlength=self.rainlength)
          LOGGER.debug("Subday computation finished")

          cols = []
          for r in self.rasters:
               cols.append('H_{}T{}'.format(r, self.rainlength))
          p = Module('v.db.select', map=map_name, flags='c',
                     columns=cols,
                     stdout_=PIPE)
          LOGGER.debug('Result: {}'.format(p.outputs.stdout))

          values = []
          for v in p.outputs.stdout.rstrip().split('|'):
               if len(v) == 0:
                    raise Exception("Bod '{0},{1}' nelezi na uzemi CR".format(
                         request.inputs['obs_x'][0].data,
                         request.inputs['obs_y'][0].data
                    ))
               values.append(float(v))

          response.outputs['output'].data = '{}'.format(
               ','.join('%.1f' % v for v in values)
          )

          return response
