import pytest
import os
import tempfile
from csv import DictReader
from pathlib import Path
from owslib.wps import WebProcessingService, monitorExecution, ComplexDataInput
from osgeo import ogr

class TestWPS:
    input_data=ComplexDataInput("http://rain.fsv.cvut.cz/geodata/test.gml")
    key="HLGP_ID"
    return_period="N2,N5,N100"
    rainlength="360"
    keycolumn="HLGP_ID"
    stype="E,F"
    value="25"
    area_size="10000"

    def _wps(self):
        return WebProcessingService('https://rain1.fsv.cvut.cz/services/wps')

    def _get_filename(self):
        return str(Path(tempfile._get_default_tempdir()) / next(tempfile._get_candidate_names()))

    def test_001_capabilities(self):
        """Test GetCapapablities."""
        processes = self._wps().processes
        assert len(processes) > 5
        assert any(process.identifier.startswith('d-rain') for process in processes)

    def _run_job(self, process, inputs, ext):
        execution = self._wps().execute(process, inputs)
        monitorExecution(execution)
        assert execution.getStatus() == "ProcessSucceeded"

        ofile = self._get_filename() + ext
        execution.getOutput(ofile)

        return ofile
        
    def _process_d_rain_output(self, ofile, fields):
        if Path(ofile).suffix == '.zip':
            dsn = '/vsizip/' + ofile
        else:
            dsn = ofile
        ds = ogr.Open(dsn)
        assert ds

        if Path(ofile).suffix == '.zip':
            assert ds.GetLayer().GetName() == "subdayprecip_output"
        else:
            assert ds.GetLayer().GetName() == Path(ofile).stem

        lyr = ds.GetLayer()
        assert lyr.GetFeatureCount() == 15

        field_names = [field.name for field in lyr.schema]

        lyr.ResetReading()
        while True:
            feat = lyr.GetNextFeature()
            if feat is None:
                break
            for f in fields:
                assert float(feat[f]) > 0

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

        self._process_d_rain_output(
            ofile,
            ['H_N2T360', 'H_N5T360', 'H_N100T360']
        )

    def test_003_d_rain_shp(self):
        """Test d-rain-shp"""
        ofile = self._run_job(
            'd-rain-shp',
            [("input", self.input_data),
             ("return_period", self.return_period),
             ("rainlength", self.rainlength),
             ("area_size", self.area_size)],
            '.zip'
        )
        self._process_d_rain_output(
            ofile,
            ["H_N2T360", "H_N5T360", "H_N100T360"]
        )

    def test_004_d_rain_csv(self):
        """Test d-rain-csv"""
        ofile = self._run_job(
            'd-rain-csv',
            [("input", self.input_data),
             ("return_period", self.return_period),
             ("rainlength", self.rainlength),
             ("keycolumn", self.keycolumn),
             ("area_size", self.area_size)],
            '.csv'
        )
        self._process_d_rain_output(
            ofile,
            ["H_N2T360_mm", "H_N5T360_mm", "H_N100T360_mm"]
        )

    def test_005_d_rain_point(self):
        """Test d-rain-point"""
        ofile = self._run_job(
            'd-rain-point',
            [("obs_x", "15.11784"),
             ("obs_y", "49.88598"),
             ("return_period", self.return_period),
             ("rainlength", self.rainlength)],
            '.txt'
        )
        with open(ofile) as fd:
            assert fd.read() == "30.2,44.2,89.0"

    def _process_d_rain6h_timedist(self, ofile):
        fields = []
        for rp in self.return_period.split(','):
            fields.append(f"H_{rp}T{self.rainlength}_mm")
            for st in self.stype.split(','):
                fields.append(f"P_{rp}typ{st}_%")
        with open(ofile) as fd:
            data = DictReader(fd)
            nlines = 0
            for row in data:
                for f in fields:
                    assert float(row[f]) > 0
                nlines += 1

            assert nlines == 15

    def test_006_d_rain6h_timedist_reduction(self):
        ofile = self._run_job(
            'd-rain6h-timedist',
            [("input", self.input_data),
             ("return_period", self.return_period),
             ("keycolumn", self.keycolumn),
             ("type", self.stype)],
            '.txt'
        )
        self._process_d_rain6h_timedist(ofile)

    def test_007_d_rain6h_timedist_reduction_disabled(self):
        ofile = self._run_job(
            'd-rain6h-timedist',
            [("input", self.input_data),
             ("return_period", self.return_period),
             ("keycolumn", self.keycolumn),
             ("type", self.stype),
             ("area_red", "false")],
            '.txt'
        )
        self._process_d_rain6h_timedist(ofile)
