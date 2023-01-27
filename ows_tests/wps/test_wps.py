import pytest
import os
import tempfile
from csv import DictReader
from pathlib import Path
from owslib.wps import WebProcessingService, monitorExecution, ComplexDataInput
from osgeo import ogr, gdal

class TestWPS:
    # url='https://rain1.fsv.cvut.cz/services/wps'
    url='http://localhost/services/wps'
    input_data=ComplexDataInput("http://rain.fsv.cvut.cz/geodata/test.gml")
    key="HLGP_ID"
    return_period=["N2","N5","N100"]
    rainlength="360"
    keycolumn="HLGP_ID"
    shape=["E", "F"]
    value="25"
    area_size="10000"

    def _wps(self, url=None):
        return WebProcessingService(
            url if url else self.url
        )

    def _request_multi(self, option):
        return [(option, x) for x in getattr(self, option)]

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

    def _run_job_request(self, request_file, ext=None, url=None,
                         exception=None):
        with open(request_file,'rb') as fd:
            request = fd.read()
        execution = self._wps(url).execute(None, [], request=request)
        monitorExecution(execution)

        if exception is None:
            assert execution.getStatus() == "ProcessSucceeded"
            ofile = self._get_filename() + ext
            execution.getOutput(ofile)
            return ofile
        else:
            assert len(execution.errors) > 0
            assert execution.getStatus() == "Exception"
            assert str(execution.errors[0].text).startswith(exception)

        return None
    
    def _process_d_rain_output(self, ofile, units=False):
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
        fields = self._get_fields(units)

        while True:
            feat = lyr.GetNextFeature()
            if feat is None:
                break
            for f in fields:
                assert float(feat[f]) > 0

        ds = None
        os.remove(ofile)

    def _get_fields(self, units):
        units_str = "_mm" if units else ""
        return [f'H_{x}T{self.rainlength}{units_str}' for x in self.return_period]

    def test_002_d_rain_shp_post(self):
        """Test d-rain-shp (post method)."""
        ofile = self._run_job_request(
            Path(__file__).parent / 'request-d-rain-shp.xml',
            '.zip'
        )

        self._process_d_rain_output(
            ofile
        )

    def test_003_d_rain_shp(self):
        """Test d-rain-shp"""
        ofile = self._run_job(
            'd-rain-shp',
            [("input", self.input_data),
             ("rainlength", self.rainlength),
             ("area_size", self.area_size)
            ] + self._request_multi("return_period"),
            '.zip'
        )
        self._process_d_rain_output(
            ofile
        )

    def test_004_d_rain_csv(self):
        """Test d-rain-csv"""
        ofile = self._run_job(
            'd-rain-csv',
            [("input", self.input_data),
             ("rainlength", self.rainlength),
             ("keycolumn", self.keycolumn),
             ("area_size", self.area_size)
            ] + self._request_multi("return_period"),
            '.csv'
        )
        self._process_d_rain_output(
            ofile,
            units=True
        )

    def test_005_d_rain_point(self):
        """Test d-rain-point"""
        ofile = self._run_job(
            'd-rain-point',
            [("obs_x", "15.11784"),
             ("obs_y", "49.88598"),
             ("rainlength", self.rainlength)
            ] + self._request_multi("return_period"),
            '.txt'
        )
        with open(ofile) as fd:
            assert fd.read() == "30.2,44.2,89.0"

    def _process_d_rain6h_timedist(self, ofile):
        fields = []
        for rp in self.return_period:
            fields.append(f"H_{rp}T{self.rainlength}_mm")
            for st in self.shape:
                fields.append(f"P_{rp}tvar{st}_%")
            for st in self.shape:
                fields.append(f"QAPI_tvar{st}")
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
             ("keycolumn", self.keycolumn),
            ] + self._request_multi("return_period") + self._request_multi("shape"),
            '.csv'
        )
        self._process_d_rain6h_timedist(ofile)

    def test_007_d_rain6h_timedist_reduction_disabled(self):
        ofile = self._run_job(
            'd-rain6h-timedist',
            [("input", self.input_data),
             ("keycolumn", self.keycolumn),
             ("area_red", "false")
            ] + self._request_multi("return_period") + self._request_multi("shape"),
            '.csv'
        )
        self._process_d_rain6h_timedist(ofile)

    def test_008_raintotal6h_timedist(self):
        ofile = self._run_job(
            'raintotal6h-timedist',
            [("value", self.value),
            ] + self._request_multi("shape"),
            '.csv'
        )
        with open(ofile) as fd:
            data = DictReader(fd)
            time = 5
            for row in data:
                assert int(row["CAS_min"]) == time
                for st in self.shape:
                    assert float(row[f"H_tvar{st}_mm"]) > 0                
                time += 5
                
    def test_009_soil_texture_hsg(self):
        ofile = self._run_job_request(
            Path(__file__).parent / 'request-soil-texture-hsg.xml',
            '.zip'
        )

        geo_transform = (-717742.5, 20.0, 0.0, -1083242.5, 0.0, -20.0)
        for name in ('sand', 'clay', 'usda-texture-class', 'silt'):
            ds = gdal.Open(f'/vsizip/{ofile}/{name}.tif')
            assert ds
            assert ds.RasterCount == 1
            assert ds.GetGeoTransform() == geo_transform
            ds = None

    def test_010_soil_texture_hsg20km2(self):
        ofile = self._run_job_request(
            Path(__file__).parent / 'request-soil-texture-hsg20km2.xml',
            exception="Process error: Limit 20km2 na vymeru zajmoveho uzemi prekrocen"
        )

    def test_011_smoderp2d_capabilities(self):
        processes = self._wps('https://rain1.fsv.cvut.cz:4444/services/wps').processes
        assert len(processes) == 2
        assert any(process.identifier.startswith('smoderp') for process in processes)

    def test_012_profile1d(self):
        ofile = self._run_job_request(        
            Path(__file__).parent / 'request-profile1d.xml',
            '.csv',
            'https://rain1.fsv.cvut.cz:4444/services/wps'
        )

        with open(ofile) as fd:
            data = DictReader(fd)
            for row in data:
                assert float(row["length[m]"]) > 0
                assert row["soilVegFID"] in ("HXGEO", "PXOP")
