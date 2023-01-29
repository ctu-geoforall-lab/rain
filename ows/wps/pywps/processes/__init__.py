# -*- coding: utf-8 -*-

####################################################################
# QJ1520265 project - source code and support files for OGC WMS and
# WPS implementation http://rain.fsv.cvut.cz
#
# Purpose: WPS processes (base class)
# Author: Martin Landa <martin.landa fsv.cvut.cz>
# Licence: see LICENCE file for details
####################################################################

import os
import sys

import time
import types
import shutil
import magic
import logging
import math
from subprocess import PIPE

from grass.pygrass.modules import Module
from grass.exceptions import CalledModuleError

from pywps import Process, ComplexInput, LiteralInput, Format, ComplexOutput, LiteralOutput, LOGGER
from pywps.app.exceptions import ProcessError
from pywps.validator.mode import MODE

class SubDayPrecipProcess(Process):
     def __init__(self, identifier, title,
                  version=1.0, abstract='',
                  location='/data/grass_location',
                  input_params=[], output_params=[]):
          
          inputs = []
          outputs = []
          if 'input' in input_params:
               inputs.append(ComplexInput(
                    identifier="input",
                    title="Vstupní (bodová či polygonová) vektorová data (mohou být zkoprimována zip/gzip, velikost souboru je omezen na 200MB)",
                    supported_formats=[Format('text/xml'), # required by QGIS WPS client
                                       Format('GML'),
                                       Format('application/zip; charset=binary')])
               )

          if 'obs' in input_params:
               inputs.append(LiteralInput(
                    identifier="obs_x",
                    title="Zeměpisná délka zájmového bodu",
                    data_type='float')
               )
               inputs.append(LiteralInput(
                    identifier="obs_y",
                    title="Zeměpisná šířka zájmového bodu",
                    data_type='float')
               )

          if 'value' in input_params:
               inputs.append(LiteralInput(
                    identifier="value",
                    title="Hodnota návrhového úhrnu 6hodinové srážky v mm",
                    data_type='float')
               )

          if 'keycolumn' in input_params:
               inputs.append(LiteralInput(
                    identifier="keycolumn",
                    title="Název vybraného atributu vstupních dat použitého jako klíčový sloupec. Tento identifikátor lze posléze použít pro připojení textového výstupu k atributovým datům vstupních dat",
                    data_type='string')
               )
          
          if 'return_period' in input_params:
               return_periods = ["N2", "N5", "N10", "N20", "N50", "N100"]

               inputs.append(LiteralInput(
                    identifier="return_period",
                    title="Požadované doby opakování",
                    data_type='string',
                    allowed_values=return_periods,
                    max_occurs=len(return_periods),
                    default=','.join(return_periods),
                    mode=MODE.NONE)
               )
          
          if 'area_size' in input_params:
               inputs.append(LiteralInput(
                    identifier="area_size",
                    title="Maximalni vymera plochy v km2 pro kterou bude navrhova srazka vypoctena (-1 pro zadny limit)",
                    data_type='float',
                    default='20',
                    min_occurs=0)
               )

          self._shapes = ['A', 'B', 'C', 'D', 'E', 'F']
          if 'shape' in input_params:
               inputs.append(LiteralInput(
                    identifier="shape",
                    title="Požadované tvary průběhu intenzit 6hodinové návrhové srážky",
                    data_type='string',
                    allowed_values=self._shapes,
                    max_occurs=len(self._shapes),
                    default=','.join(self._shapes),
                    mode=MODE.NONE)
               )

          if 'area_red' in input_params:
               inputs.append(LiteralInput(
                    identifier="area_red",
                    title="Logický přepínač pro kontrolu plochy vstupních prvků a provádění redukce úhrnů",
                    data_type='boolean',
                    default='true',
                    min_occurs=0)
               )

          if 'cn' in input_params:
               inputs.append(LiteralInput(
                    identifier="cn2",
                    title="Hodnota CN",
                    data_type='float')
               )
               
          if 'ia' in input_params:
               inputs.append(LiteralInput(
                    identifier="Ia",
                    title="Hodnota Ia",
                    data_type='float',
                    default="0.2")
               )
               
          if 'output_volume' in output_params:
               outputs.append(LiteralOutput(
                    identifier="output",
                    title="Hodnota objemu",
                    data_type='string')
               )

          if 'output_probabilities' in output_params:
               outputs.append(ComplexOutput(
                    identifier="output",
                    title="Vyčíslené hodnoty pravděpodobnosti tvaru pětiminutových intenzit návrhových srážek pro vstupní vektorové prvky ve formátu CSV",
                    supported_formats=[Format('text/csv')],
                    as_reference = True)
               )

          if 'output_shapes' in output_params:
               outputs.append(ComplexOutput(
                    identifier="output_shapes" if identifier == "d-rain6h-timedist" else "output",
                    title="Vyčíslené průběhy pětiminutových intenzit návrhových srážek pro vstupní vektorové prvky ve formátu CSV",
                    supported_formats=[Format('text/csv')],
                    as_reference = True)
               )

          super(SubDayPrecipProcess, self).__init__(
               self._handler,
               identifier=identifier,
               version=version,
               title=title,
               abstract=abstract,
               inputs=inputs,
               outputs=outputs,
               grass_location=location,
               store_supported=True,
               status_supported=True)

          self.map_name = None
          self.keycolumn = None
          self.return_period = None
          self.rainlength = None
          self.shapetype = None

          self.output = None # to be defined by descendant
          self.output_dir = None
          
          os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
          os.environ['HOME'] = '/tmp' # needed by G_home()

     # def __del__(self):
     #      if self.output_dir:
     #           shutil.rmtree(self.output_dir)

     def _handler(self, request, response):
          if 'keycolumn' in request.inputs.keys():
               self.keycolumn = request.inputs['keycolumn'][0].data
          if 'return_period' in request.inputs.keys():
               self.return_period = [rp.data.strip() for rp in request.inputs['return_period']]
          if 'rainlength' in request.inputs.keys():
               self.rainlength = request.inputs['rainlength'][0].data
          if 'shape' in request.inputs.keys():
               self.shapetype = [st.data.strip() for st in request.inputs['shape']]
          if 'area_size' in request.inputs.keys():
               self.area_size = request.inputs['area_size'][0].data
          else:
               self.area_size = 20
          if 'area_red' in request.inputs.keys():
               self.area_red = request.inputs['area_red'][0].data
          else:
               self.area_red = True
          if 'input' in request.inputs.keys():
               self.map_name = self.import_data(request.inputs['input'][0].file)
          if 'obs_x' in request.inputs.keys():
               self.map_name = self.point_map_from_obs(
                    request.inputs['obs_x'][0].data,
                    request.inputs['obs_y'][0].data)
          if 'keycolumn' in request.inputs.keys():
               self.check_keycolumn(self.keycolumn)

          if 'cn2' in request.inputs.keys():
               self.cn2 = request.inputs['cn2'][0].data
          if 'ia' in request.inputs.keys():
               self.ia = request.inputs['ia'][0].data
          else:
               self.ia = 0.2

          self.output_dir = os.path.join('/tmp', '{}_{}'.format(
               self.identifier, os.getpid())
          )
          if os.path.exists(self.output_dir):
               shutil.rmtree(self.output_dir)
          os.mkdir(self.output_dir)

          self._response = response # report_progress() can be called by other methods

          # set computational region
          Module('g.region', raster="H_N2T360@rain6h")

          if self.map_name:
               LOGGER.debug("Computation started")
               
               start = time.time()
               self.report_progress(1, "Starting computation")

               LOGGER.info("R: {}".format(self.rainlength))
               
               if self.identifier == 'd-rain6h-timedist':
                    self._v_rast_stats(self.area_red)
               elif self.identifier == 'cn-rain6h':
                    self.compute_volume(self.cn2, self.ia)
                    
               LOGGER.info("Computation finished: {} sec".format(time.time() - start))

          # export output
          if self.identifier == 'd-rain6h-timedist':
               response.outputs['output_shapes'].file, response.outputs['output'].file = \
                    self.export()
          else:
               response.outputs['output'].file = self.export()
          self.report_progress(100, "Computation finished")

          del self._response

          return response

     def report_progress(self, value, message=None):
          self._response.update_status(
               message='Computation progress' if message is None else message,
               status_percentage=int(value)
          )

     def _area_size_reduction(self, map_name, field_name, area_col_name):
          """Taken from r.subdayprecip.design"""
          from grass.pygrass.gis import Mapset
          from grass.pygrass.vector import VectorTopo

          mapset = Mapset()
          # very strangely, current mapset can be reported by pygrass wrongly
          import grass.script as gscript
          cur_mapset = gscript.gisenv()['MAPSET']
          if mapset.name != cur_mapset:
               mapset = Mapset(cur_mapset)
               mapset.current()
          with VectorTopo(map_name, mapset=cur_mapset) as vmap:
               cats = [] # TODO: do it better
               for feat in vmap.viter('areas'):
                    if not feat.attrs or feat.attrs[field_name]:
                         continue
                    if feat.attrs['cat'] not in cats:
                         x = math.log10(float(feat.attrs[area_col_name]) ) - 0.9
                         k = math.exp(-0.08515989 * pow(x, 2) - 0.001344925 * pow(x, 4))
                         feat.attrs[field_name] *= k
                         cats.append(feat.attrs['cat'])

               vmap.table.conn.commit()

     def _v_rast_stats(self, reduction=True):
          columns = []

          area_col_name = 'area_{}'.format(os.getpid())
          # check area size limit
          Module('v.to.db', map=self.map_name, option='area',
                 columns=area_col_name, units='kilometers'
          )

          LOGGER.info("Reduction enabled?: {}".format(reduction))

          i = 1
          count = len(self.return_period)
          for rp in self.return_period:
               self.report_progress(i * 20/count, f"Computing {rp}")

               n = rp.lstrip('N')
               col_name = 'H_N{n}T360'.format(n=n)
               rast_name = 'H_N{n}T360@{ms}'.format(
                    n=n, ms=self.mapset
               )
               self.v_rast_stats(rast_name, col_name)

               Module('v.db.renamecolumn', map=self.map_name,
                      column=[col_name + '_average', col_name]
               )
               if reduction:
                    self._area_size_reduction(
                         self.map_name, col_name, area_col_name
                    )
               # else:
               #      Module('v.db.update', map=self.map_name,
               #             column=col_name, value='-1',
               #             where='{} > {}'.format(area_col_name, self.area_size)
               #      )
               i += 1

          # cleanup
          Module('v.db.dropcolumn', map=self.map_name,
                 columns=area_col_name
          )

     def v_rast_stats(self, rast_name, col_name):
          try:
               Module('v.rast.stats', map=self.map_name, raster=rast_name,
                      method='average', column_prefix=col_name
               )
               null_values = Module('v.db.select', map=self.map_name, columns='cat', flags='c',
                                    where="{}_average is NULL".format(col_name), stdout_=PIPE)
               cats = null_values.outputs.stdout.splitlines()
          except CalledModuleError:
               cats = [1] # no category found, use pseudo category to call v.what.rast
               
          # handle NULL values (areas smaller than raster resolution)
          LOGGER.info("Number of small areas: {} (raster: {} column {})".format(
               len(cats), rast_name, col_name))

          if len(cats) > 0:
               Module('v.what.rast', map=self.map_name, raster=rast_name, type='centroid',
                      column='{}_average'.format(col_name), where="{}_average is NULL".format(col_name)
               )
          
     def check_keycolumn(self, keycol):
          # check if key columns exists
          map_cols = Module('db.columns',
                            table=self.map_name, stdout_=PIPE).outputs.stdout.splitlines()
          if keycol not in map_cols:
               raise StandardError(
                    "Key column ({}) not found in input attribute table ({})".format(
                    keycol, ','.join(map_cols))
               )
          
     def import_data(self, input_data, link_only=False):
          map_name = 'subdayprecip_output'

          try:
               mime_type = magic.detect_from_filename(input_data).mime_type
          except AttributeError:
               mime_type = magic.from_file(input_data, mime=True)

          prefix = '/'
          ext = ''
          if mime_type.endswith('gzip'):
               prefix += 'vsigzip/'
               ext = '.gz'
          elif mime_type.endswith('zip'):
               prefix += 'vsizip/'
               ext = '.zip'
          if ext:
               # GDAL requires extension (why?)
               os.rename(input_data, input_data + ext)
          input_data = prefix + input_data + ext

          # link or import ?
          module_in_args = {}
          module_in_args['input'] = input_data
          if link_only:
               module_in = 'v.external'
               module_in_args['layer'] = 'basin' # TODO: fix it!
          else:
               module_in = 'v.in.ogr'
               # skip projection check
               module_in_args['flags'] = 'o'
               # snap to 1cm (assuming ArcGIS data)
               module_in_args['snap'] = 0.01

          LOGGER.debug("Import started ({})".format(input_data))
          start = time.time()
          try:
               Module(module_in,
                      output=map_name,
                      overwrite=True,
                      **module_in_args
               )
          except CalledModuleError as e:
               with open(input_data) as fd:
                    LOGGER.info("Input data content: {}".format(fd.read()))
               raise ProcessError("Unable to import input vector data - {}".format(e))
          
          LOGGER.info("Input data imported ({}): {} sec".format(
               module_in, time.time() - start)
          )
          
          return map_name
     
     def export(self):
          pass

     def point_map_from_obs(self, obs_x, obs_y):
          map_name = "input_point_map"
          vector_input="1|{}|{}".format(obs_x, obs_yy)
          LOGGER.debug('Input: {}'.format(vector_input))
          Module('v.in.ascii', input='-', output=map_name,
                 cat=1, x=2, y=3, stdin_=vector_input)
          Module('v.db.addtable', map=map_name)
          
          return input_point_map
