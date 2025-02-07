import io
from owslib.wfs import WebFeatureService
from osgeo import ogr

class TestWFS:
    url='https://rain1.fsv.cvut.cz/services/wfs'
    #url='http://localhost/services/wfs'

    wfs_version = '1.1.0'
    wfs_layer = 'bpej'
    wfs_bbox = (-834049.1, -1099502.9, -832994.7, -1099073.9)
    
    def _wfs(self, url=None):
        return WebFeatureService(
            url if url else self.url,
            version=self.wfs_version
        )

    def test_001_capabilities(self):
        """Test GetCapapablities."""
        wfs = self._wfs()

        assert wfs.identification.version == self.wfs_version
        assert len(list(wfs.contents)) == 1
        assert wfs.contents[self.wfs_layer].title == 'Celostátní databáze BPEJ'

    def test_002_getfeature(self):
        """Test GetFeatureRequest."""
        response = self._wfs().getfeature(typename=self.wfs_layer, bbox=self.wfs_bbox)
        with open('/tmp/data.gml', 'wb') as out:
            out.write(response.read())
        ds = ogr.Open('/tmp/data.gml')
        assert ds is not None
        assert ds.GetLayerCount() == 1
        assert ds.GetLayer().GetFeatureCount() > 0
