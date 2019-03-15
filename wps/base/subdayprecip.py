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

os.environ['GISBASE'] = '/opt/grass/dist.x86_64-pc-linux-gnu'
sys.path.append(os.path.join(os.environ["GISBASE"], "etc", "python"))
os.environ['LD_LIBRARY_PATH'] = os.path.join(os.environ["GISBASE"], "lib")

from grass.pygrass.gis import Mapset
from grass.pygrass.modules import Module
from grass.pygrass.vector import VectorTopo
from grass.exceptions import CalledModuleError

from pywps import Process, ComplexInput, LiteralInput, Format, ComplexOutput, LiteralOutput

LOGGER = logging.getLogger('PYWPS')

class SubDayPrecipProcess(Process):
     def __init__(self, identifier, description,
                  location='/opt/grassdata/subdayprecip',
                  input_params=[], output_params=[]):
          inputs = []
          outputs = []
          if 'input' in input_params:
               inputs.append(ComplexInput(
                    identifier="input",
                    title=u"Vstupni bodova nebo polygonova vektorova data",
                    supported_formats=[Format('text/xml'), # requires QGIS WPS client
                                       Format('GML'),
                                       Format('application/zip; charset=binary')])
               )

          if 'obs' in input_params:
               inputs.append(LiteralInput(
                    identifier="obs_x",
                    title=u"Zemepisna delka zajmoveho bodu",
                    data_type='float')
               )
               inputs.append(LiteralInput(
                    identifier="obs_y",
                    title=u"Zemepisna sirka zajmoveho bodu",
                    data_type='float')
               )

          if 'value' in input_params:
               inputs.append(LiteralInput(
                    identifier="value",
                    title=u"Hodnota navrhove srazky v mm",
                    data_type='float')
               )

          if 'keycolumn' in input_params:
               inputs.append(LiteralInput(
                    identifier="keycolumn",
                    title=u"Klicovy atribut vstupnich dat",
                    data_type='string')
               )
          
          if 'return_period' in input_params:
               inputs.append(LiteralInput(
                    identifier="return_period",
                    title=u"Doby opakovani",
                    data_type='string',
                    default="N2,N5,N10,N20,N50,N100")
               )
          
          if 'rainlength' in input_params:
               inputs.append(LiteralInput(
                    identifier="rainlength",
                    title=u"Delka srazky v minutach",
                    data_type='integer')
               )

          if 'area_size' in input_params:
               inputs.append(LiteralInput(
                    identifier="area_size",
                    title=u"Maximalni vymera plochy v km2 pro kterou bude navrhova srazka vypoctena (-1 pro zadny limit)",
                    data_type='float',
                    default='20',
                    min_occurs=0)
               )

          if 'area_red' in input_params:
               inputs.append(LiteralInput(
                    identifier="area_red",
                    title=u"Provést redukci úhrnu pro povodí nad 20 km2",
                    data_type='boolean',
                    default='true',
                    min_occurs=0)
               )

          if 'type' in input_params:
               inputs.append(LiteralInput(
                    identifier="type",
                    title=u"Typy rozlozeni srazky",
                    data_type='string',
                    default='A,B,C,D,E,F')
               )

          if 'output_shp' in output_params:
               outputs.append(ComplexOutput(
                    identifier="output",
                    title=u"Vysledek ve formatu Esri Shapefile",
                    supported_formats=[Format('application/x-zipped-shp')],
                    as_reference=True)
               )

          if 'output_csv' in output_params:
               outputs.append(ComplexOutput(
                    identifier="output",
                    title=u"Vysledek ve formatu CSV",
                    supported_formats=[Format('application/csv')],
                    as_reference = True)
               )

          if 'output_value' in output_params:
               outputs.append(LiteralOutput(
                    identifier="output",
                    title=u"Vycislena hodnota navrhove srazky v mm",
                    data_type='string')
               )

          if 'output_shapes' in output_params:
               outputs.append(ComplexOutput(
                    identifier="output",
                    title=u"Vysledne hodnoty prubehu navrhovych srazek ve formatu CSV",
                    supported_formats=[Format('application/csv')],
                    as_reference = True)
               )
          
          super(SubDayPrecipProcess, self).__init__(
               self._handler,
               identifier=identifier,
               version="0.1",
               title=u"Navrhova srazka pro zvolenou lokalitu. " + description,
               abstract=u"Pocita navrhovou srazku pro zvolenou lokalitu s vyuzitim nastroje GRASS GIS r.subdayprecip.design. Vice informaci na http://rain.fsv.cvut.cz/nastroje/r.subdayprecip.design",
               inputs=inputs,
               outputs=outputs,
               grass_location=location,
               store_supported=True,
               status_supported=True)

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
               self.return_period = request.inputs['return_period'][0].data.split(',')
          if 'rainlength' in request.inputs.keys():
               self.rainlength = request.inputs['rainlength'][0].data
          if 'type' in request.inputs.keys():
               self.shapetype = request.inputs['type'][0].data.split(',')
          if 'value' in request.inputs.keys():
               self.value = request.inputs['value'][0].data
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
          
          if 'keycolumn' in request.inputs.keys():
               self.check_keycolumn(self.keycolumn)

          self.output_dir = os.path.join('/tmp', '{}_{}'.format(
               self.identifier, os.getpid())
          )
          if os.path.exists(self.output_dir):
               shutil.rmtree(self.output_dir)
          os.mkdir(self.output_dir)

          if 'input' in request.inputs.keys():
               LOGGER.debug("Subday computation started")
               start = time.time()
               LOGGER.info("R: {}".format(self.rainlength))
               if self.identifier == 'd-rain6h-timedist':
                    LOGGER.info('Using v.rast.stats')
                    self._v_rast_stats(self.area_red)
               else:
                    LOGGER.info('Using r.subdayprecip.design')
                    Module('g.region', raster=self.return_period[0])
                    Module('r.subdayprecip.design',
                           map=self.map_name, return_period=self.return_period,
                           rainlength=self.rainlength, area_size=self.area_size
                    )
               LOGGER.info("Subday computation finished: {} sec".format(time.time() - start))

          response.outputs['output'].file = self.export()

          return response

     def _area_size_reduction(self, map_name, field_name, area_col_name):
          """Taken from r.subdayprecip.design"""
          mapset = Mapset()
          # very strangely, current mapset can be reported by pygrass wrongly
          import grass.script as gscript
          cur_mapset = gscript.gisenv()['MAPSET']
          if mapset.name != cur_mapset:
               mapset = Mapset(cur_mapset)
               mapset.current()
          vmap = VectorTopo(map_name, mapset=cur_mapset)
          vmap.open('rw')

          cats = [] # TODO: do it better
          for feat in vmap.viter('areas'):
               if not feat.attrs or feat.attrs[field_name]:
                    continue
               if feat.attrs['cat'] not in cats:
                    x = math.log10(float(feat.attrs[area_col_name]) )- 0.9
                    k = math.exp(-0.08515989 * pow(x, 2) - 0.001344925 * pow(x, 4))
                    feat.attrs[field_name] *= k
                    cats.append(feat.attrs['cat'])

          vmap.table.conn.commit()
          vmap.close()

     def _v_rast_stats(self, reduction=True):
          columns = []

          area_col_name = 'area_{}'.format(os.getpid())
          # check area size limit
          Module('v.db.addcolumn', map=self.map_name,
                 columns='{} double precision'.format(area_col_name)
          )
          Module('v.to.db', map=self.map_name, option='area',
                 columns=area_col_name, units='kilometers'
          )

          LOGGER.info("Reduction enabled?: {}".format(reduction))

          for rp in self.return_period:
               n = rp.lstrip('N')
               col_name = 'H_N{n}T360'.format(n=n)
               rast_name = 'sjtsk_navrhove_srazky_6h_P_{n}yr_6h_mm@{ms}'.format(
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
          LOGGER.info("Number of small areas: {}".format(len(cats)))
          
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
          if link_only:
               module_in = 'v.external'
               module_in_args['input'] = input_data
               module_in_args['layer'] = 'basin' # TODO: fix it!
          else:
               module_in = 'v.in.ogr'
               module_in_args['input'] = input_data
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
               raise Exception("Unable to import input vector data: {}".format(e))
          
          LOGGER.info("Input data imported ({}): {} sec".format(
               module_in, time.time() - start)
          )
          
          return map_name
     
     # def copy(self):
     #      map_name = request.inputs['input'][0].data
     #      Module('g.copy', vector=['{}@PERMANENT'.format(map_name),map_name],
     #             overwrite=True
     #      )

     #      return map_name
     
     def export(self):
          pass
