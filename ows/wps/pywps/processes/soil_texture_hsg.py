import os
import shutil
from subprocess import PIPE

from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, LOGGER
from pywps.app.exceptions import ProcessError
from pywps.validator.mode import MODE

from grass.exceptions import CalledModuleError
from grass.pygrass.modules import Module

class SoilTextureHsg(Process):
    def __init__(self):
        self.layers = ["hsg", "usda-texture-class", "sand", "silt", "clay"]
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
                max_occurs=len(self.layers),
                default=','.join(self.layers[:2]),
                mode=MODE.NONE
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

        super().__init__(
            self._handler,
            identifier="soil-texture-hsg",
            version="1.0",
            # title="Nástroj soil-texture-hsg slouží ke stažení výřezu rastrových dat půdních vlastností pro polygon o výměře do 20 km2.",
            # abstract="Nástroj soil-texture-hsg slouží ke stažení výřezu rastrových dat půdních vlastností pro polygon o výměře do 20 km2. Konkrétně se jedná o tři vrstvy procentuálního zastoupení frakcí písku, prachu a jílu, jednu vrstvu zrnitosti s členěním do 12 tříd dle USDA metodiky a jednu vrstvu hydrologické půdní skupiny. Podkladová data byla odvozena metodami digitálního mapování v rámci projektu Fyzikální a hydropedologické vlastnosti půd ČR.",
            title="Nastroj soil-texture-hsg slouzi ke stazeni vyrezu rastrovych dat pudnich vlastnosti pro polygon o vymere do 20 km2.",
            abstract="Nastroj soil-texture-hsg slouzi ke stazeni vyrezu rastrovych dat pudnich vlastnosti pro polygon o vymere do 20 km2. Konkretne se jedna o tri vrstvy procentualniho zastoupeni frakci pisku, prachu a jilu, jednu vrstvu zrnitosti s clenenim do 12 trid dle USDA metodiky a jednu vrstvu hydrologicke pudni skupiny. Podkladova data byla odvozena metodami digitalniho mapovani v ramci projektu Fyzikalni a hydropedologicke vlastnosti pud CR.",
            inputs=inputs,
            outputs=outputs,
            grass_location="/data/grass_location",
            store_supported=True,
            status_supported=True)

        self.area_limit = 20 # km2

        self.mapset = "soil_texture_hsg"
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
        Module("g.region", vector=aoi, align="sand@{}".format(self.mapset))
        Module("r.mask", vector=aoi)

        # export data
        for lyr in layers:
            Module("r.out.gdal", flags="c",
                   input="{}@{}".format(lyr, self.mapset),
                   output=os.path.join(output_dir, lyr + ".tif"))
            # copy style
            shutil.copy(
                "/data/styles/{}.qml".format(lyr),
                os.path.join(output_dir, "{}.qml".format(lyr))
            )

        # zip output dir
        shutil.make_archive(output_dir, 'zip', output_dir)

        response.outputs['output'].file= output_dir + ".zip"
