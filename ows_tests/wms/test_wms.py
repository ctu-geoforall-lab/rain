import io
from owslib.wms import WebMapService
from PIL import Image
        
class TestWMS:
    # url='https://rain1.fsv.cvut.cz/services/wps'
    url='http://localhost/services/wms'

    wms_version = '1.3.0'
    wms_layer = 'H_N2_24h'
    wms_bbox = (-907000.0, -1230000.0, -429000.0, -933000.0)
    wms_size = (600, 400)

    def _wms(self, url=None):
        return WebMapService(
            url if url else self.url,
            version=self.wms_version
        )

    def test_001_capabilities(self):
        """Test GetCapapablities."""
        wms = self._wms()

        assert wms.identification.version == self.wms_version
        assert len(list(wms.contents)) == 12
        assert wms.contents[self.wms_layer].title == '2-leté maximální denní úhrny'
        print(wms.contents[self.wms_layer].boundingBox)
        
    def test_002_getmap(self):
        img = self._wms().getmap(
            layers=[self.wms_layer],
            size=self.wms_size,
            srs="EPSG:5514",
            bbox=self.wms_bbox,
            format="image/jpeg")

        image = Image.open(io.BytesIO(img.read()))
        assert image.size == self.wms_size
