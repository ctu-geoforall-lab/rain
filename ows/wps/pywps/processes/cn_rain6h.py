import os
import shutil
from subprocess import PIPE

from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, LOGGER
from pywps.app.exceptions import ProcessError
from pywps.validator.mode import MODE

from grass.exceptions import CalledModuleError
from grass.pygrass.modules import Module

from . import SubDayPrecipProcess, LOGGER

class CnRain6h(SubDayPrecipProcess):
    def __init__(self):
        SubDayPrecipProcess.__init__(
            self,
            identifier="cn-rain6h",
            title="TBD",
            abstract="",
            input_params=['obs', 'return_period', 'cn', 'ia'],
            output_params=['output_volume'],
            version=1.0
        )
        
        os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
        os.environ['HOME'] = '/tmp' # needed by G_home()

    def _scs_cn_volume(CN, Lambda, H_s, area):
        # cn is the curve number
        # i is the rainfall (mm)
        # in [ha]
        # return V [m3]

        A = 25.4 * ((1000/CN) - 10)
        I_a = Lambda * A
        if H_s > I_a:
            H_O = ((H_s - I_a) * (H_s - I_a))/(H_s - I_a + A)
        else:
            H_O = 0

        V = H_O * area

        return V

    def compute_volume(self, CN2, IA):
        CN3  = 23 * CN2 / (10 + 0.13 * CN2)

        region_set = False
        for shape in self._shapes:
            rast_name = f"a06_t{shape}z_1"
            Module('g.region',
                   raster=rast_name)
            Module('v.what.rast',
                   map=self.map_name,
                   raster=rast_name)
            v_what_rast = Module('v.db.select',
                                 map=self.map_name,
                                 columns=rast_name, flags='c',
                                 stdout_=PIPE)
            rast_val = v_what_rast.outputs.stdout

            LOGGER.info(f"{shape}: {rast_val}")
        
