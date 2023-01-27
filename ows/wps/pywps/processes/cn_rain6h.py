import os
import shutil
from subprocess import PIPE

from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, LOGGER
from pywps.app.exceptions import ProcessError
from pywps.validator.mode import MODE

from grass.exceptions import CalledModuleError
from grass.pygrass.modules import Module

class CnRain6h(Process):
    def __init__(self):
        inputs = [
        ]
        outputs = [
        ]

        super().__init__(
            self._handler,
            identifier="cn-rain6h",
            version="1.0",
            title="TBD",
            abstract="TBD",
            inputs=inputs,
            outputs=outputs,
            grass_location="/data/grassdata/TBD",
            store_supported=True,
            status_supported=True)

        os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
        os.environ['HOME'] = '/tmp' # needed by G_home()
        
    def _handler(self, request, response):
        pass
