import os
import shutil
from subprocess import PIPE

from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, LOGGER
from pywps.app.exceptions import ProcessError

from grass.exceptions import CalledModuleError
from grass.pygrass.modules import Module

class SoilTextureHsgProcess(Process):
    def __init__(self):
        self.layers = ["sand", "silt", "clay", "usda-texture-class"]
        inputs = [
            ComplexInput(
                identifier="input",
                title="Zajmove uzemi definovane polygonem do 20 km2",
                supported_formats=[Format('text/xml'), # requires by QGIS WPS client
                                   Format('GML'),
                                   Format('application/zip; charset=binary')]
            ),
            LiteralInput(
                identifier="layers",
                title="Vrstvy hydropedologickych charakteristik ({})".format(",".join(self.layers)),
                data_type='string',
                allowed_values=self.layers,
                max_occurs=len(self.layers)
            )
        ]
        outputs = [
            ComplexOutput(
                identifier="output",
                title="Vysledny vyrez rastru hydropedologickych charakteristik (ZIP)",
                supported_formats=[Format('application/zip; charset=binary')],
                as_reference=True
            )
        ]

        super(SoilTextureHsgProcess, self).__init__(
            self._handler,
            identifier="soil-texture-hsg",
            version="1.0",
            title="Zrnitost a hydrologicka skupina pudy",
            abstract="Sluzba vraci vyrez rastru zvolene hydropedologicke charakteristiky dle zadaneho polygonu o velikosti do 20 km2.",
            inputs=inputs,
            outputs=outputs,
            grass_location="/data/grassdata/soil_texture_hsg",
            store_supported=True,
            status_supported=True)

        self.area_limit = 20 # km2

        os.environ['GRASS_SKIP_MAPSET_OWNER_CHECK'] = '1'
        os.environ['HOME'] = '/tmp' # needed by G_home()
        
    def _handler(self, request, response):
        # check layers
        layers = [l.data.strip() for l in request.inputs['layers']]
        for lyr in layers:
            if lyr not in self.layers:
                raise ProcessError("Neplatna vrstva: {}".format(lyr))
        
        output_dir = os.path.join('/tmp', '{}_{}'.format(
            self.identifier, os.getpid())
        )
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)

        # import input vector map
        input_data = request.inputs['input'][0].file
        aoi = "aoi"
        try:
            Module("v.import",
                   input=input_data,
                   output=aoi,
                   overwrite=True
            )
        except CalledModuleError as e:
            # try also v.in.ogr with -f flag
            try:
                LOGGER.info("Unable to import input vector data. Projection check skipped")
                Module("v.in.ogr",
                       flags="o",
                       input=input_data,
                       output=aoi,
                       overwrite=True
                       )
            except CalledModuleError as e:
                with open(input_data) as fd:
                    LOGGER.info("Input data content: {}".format(fd.read()))
                raise ProcessError("Unable to import input vector data - {}".format(e))

        # check aoi limit
        v_to_db = Module("v.to.db", flags="pc", map=aoi, option="area", stdout_=PIPE)
        area = float(v_to_db.outputs.stdout.splitlines()[-1].split('|')[1]) / 1e6
        LOGGER.info("Area (km2): {}".format(area))
        if area > self.area_limit:
            raise ProcessError("Limit 20km2 na vymeru zajmoveho uzemi prekrocen ({})".format(
                area, self.area_limit
            ))

        # set computational region
        Module("g.region", vector=aoi, align="sand")
        Module("r.mask", vector=aoi)

        # export data
        for lyr in layers:
            Module("r.out.gdal", flags="c",
                   input=lyr, output=os.path.join(output_dir, lyr + ".tif"))
            # copy style
            shutil.copy(
                "/data/styles/{}.qml".format(lyr),
                os.path.join(output_dir, "{}.qml".format(lyr))
            )

        # zip output dir
        shutil.make_archive(output_dir, 'zip', output_dir)

        response.outputs['output'].file= output_dir + ".zip"
