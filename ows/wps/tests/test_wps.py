import pytest
import os
import tempfile
from pathlib import Path
from owslib.wps import WebProcessingService, monitorExecution, ComplexDataInput
from osgeo import ogr

class TestWPS:
    def _wps(self):
        return WebProcessingService('https://rain1.fsv.cvut.cz/services/wps')

    def _get_filename(self):
        return str(Path(tempfile._get_default_tempdir()) / next(tempfile._get_candidate_names()))

    def test_001_capabilities(self):
        """Test GetCapapablities."""
        processes = self._wps().processes
        assert len(processes) > 5
        assert any(process.identifier.startswith('d-rain') for process in processes)

    def _test_d_rain_shp_output(self, ofile, fields):
        ds = ogr.Open('/vsizip/' + ofile)
        assert ds

        assert ds.GetLayer().GetName() == "subdayprecip_output"

        lyr = ds.GetLayer()
        assert lyr.GetFeatureCount() == 15

        field_names = [field.name for field in lyr.schema]

        lyr.ResetReading()
        while True:
            feat = lyr.GetNextFeature()
            if feat is None:
                break
            for f in fields:
                assert feat[f] > 0

        ds = None
        os.remove(ofile)

    def test_002_d_rain_shp_post(self):
        """Test d-rain-shp (post method)."""
        with open('./ows/wps/tests/request-d-rain-shp.xml','rb') as fd:
            request = fd.read()
        execution = self._wps().execute(None, [], request=request)
        monitorExecution(execution)
        assert execution.getStatus() == "ProcessSucceeded"
        ofile = self._get_filename() + '.zip'
        execution.getOutput(ofile)

        self._test_d_rain_shp_output(
            ofile,
            ['H_N2T360', 'H_N5T360', 'H_N100T360']
        )

    def test_003_d_rain_shp(self):
        """Test d-rain-shp"""
        inputs = [
            ("input", ComplexDataInput('http://rain.fsv.cvut.cz/geodata/test.gml')),
            ("return_period", "N2,N5,N10"),
            ("rainlength", "360"),
            ("area_size", "10000")
        ]
        execution = self._wps().execute('d-rain-shp', inputs)
        monitorExecution(execution)
        assert execution.getStatus() == "ProcessSucceeded"

        ofile = self._get_filename() + '.zip'
        execution.getOutput(ofile)
        self._test_d_rain_shp_output(
            ofile,
            ["H_N2T360", "H_N5T360", "H_N10T360"]
        )
