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
            abstract="TBD",
            input_params=['obs', 'return_period', 'area', 'cn', 'ia'],
            output_params=['output_volume'],
            version=1.0
        )

        self.mapset = 'rain6h'

        os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
        os.environ['HOME'] = '/tmp' # needed by G_home()

    @staticmethod
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

    @staticmethod
    def _reclass_qapi(qAPI):
        if qAPI < 0.2:
            nsa = 1
        elif qAPI >=0.2 and qAPI < 0.4:
            nsa = 0.75
        elif qAPI >= 0.4 and qAPI < 0.6:
            nsa = 0.5
        elif qAPI >= 0.6 and qAPI < 0.8:
            nsa = 0.25
        else:
            nsa = 0

        return nsa
    
    def _get_value_from_raster(self, rast_name):
        Module('v.what.rast',
               map=self.map_name,
               raster=f"{rast_name}@{self.mapset}",
               column=rast_name)
        v_what_rast = Module('v.db.select',
                             map=self.map_name,
                             columns=rast_name, flags='c',
                             stdout_=PIPE)
        return float(v_what_rast.outputs.stdout.splitlines()[0])
            
    def compute_volume(self, CN2, IA, area):
        CN3  = 23 * CN2 / (10 + 0.13 * CN2)

        # get raster values
        raster_value = {}
        progress_message = "Getting values from raster layers..."
        self.report_progress(10, progress_message)
        for rp in self.return_period:
            rp = rp.lstrip('N')
            rast_name = f"H_N{rp}T360"
            raster_value[rast_name] = self._get_value_from_raster(rast_name)
            for shape in self._shapes:
                rast_name = f"{shape}_{int(rp):03d}"
                raster_value[rast_name] = self._get_value_from_raster(rast_name) / 100

        self.report_progress(35, progress_message)
        for shape in self._shapes:
            rast_name = f"a06_t{shape}z_1"
            raster_value[rast_name] = self._get_value_from_raster(rast_name)
        self.report_progress(70, progress_message)

        LOGGER.info(f"{shape}: {raster_value}")

        self._result = []
        self.report_progress(70, "Computing volume...")
        for rp in self.return_period:
            rp = rp.lstrip('N')
            rast_name = f"H_N{rp}T360"
            VCN2 = self._scs_cn_volume(CN2, IA, raster_value[rast_name], area)
            VCN3 = self._scs_cn_volume(CN3, IA, raster_value[rast_name], area)

            V = 0
            for shape in self._shapes:
                nsa = self._reclass_qapi(raster_value[f"a06_t{shape}z_1"])
                V += nsa * raster_value[f"{shape}_{int(rp):03d}"] * VCN2
                V += (1 - nsa) * raster_value[f"{shape}_{int(rp):03d}"] * VCN3
            self._result.append(V)

    def export(self):
        # export csv
        # sep = ','
        # self.output = '{}/{}.csv'.format(self.output_dir, self.identifier)
        # with open(self.output, 'w') as fp:
        #     for rp in self.return_period:
        #         fp.write(f'V_{rp}_m3{sep}')
        #     fp.write('\r\n')
        #     for v in self._result:
        #         fp.write(f'{v:.3f}{sep}')
        #     fp.write('\r\n')

        LOGGER.info(f"Result {self._result}")
        self.output = ','.join(f'{v:.2f}' for v in self._result)
        return self.output
