import pytest
import os
import tempfile
import json
from csv import DictReader
from pathlib import Path
from owslib.wps import WebProcessingService, monitorExecution, ComplexDataInput
from osgeo import ogr, gdal

class TestWPS:
    url='https://rain1.fsv.cvut.cz/services/wps'
    # url='http://localhost:8084/services/wps'
    input_data=ComplexDataInput("http://rain.fsv.cvut.cz/geodata/test.gml")
    dump_ofile=False
    
    key="HLGP_ID"
    return_period=["N2","N5","N100"]
    rainlength="360"
    keycolumn="HLGP_ID"
    type=["E", "F"]
    value="25"
    area_size="10000"
    num_processes = 4
    obs_x="13.9705854384"
    obs_y="49.8800531434"
    cn2="81"
    area="5.7"
    lambda_="0.2"

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
        assert len(processes) == self.num_processes
        assert any(process.identifier.startswith('d-rain6h') for process in processes)

    def _dump_ofile(self, filename):
        if not self.dump_ofile or Path(filename).suffix == '.zip':
            return
        with open(filename, 'r') as fd:
            print(fd.read())

    def _run_job(self, process, inputs, ext=None, exception=None):
        execution = self._wps().execute(process, inputs)
        monitorExecution(execution)
        if exception is None:
            assert execution.getStatus() == "ProcessSucceeded"
            if ext:
                ofile = self._get_filename() + ext
                execution.getOutput(ofile)
                self._dump_ofile(ofile)

                return ofile
        else:
            assert len(execution.errors) > 0
            assert execution.getStatus() == "Exception"
            assert str(execution.errors[0].text).startswith(exception)

        return None

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
            self._dump_ofile(ofile)

            return ofile
        else:
            assert len(execution.errors) > 0
            assert execution.getStatus() == "Exception"
            assert str(execution.errors[0].text).startswith(exception)

        return None
    
    def _process_d_rain6h_timedist(self, ofile):
        fields = []
        for rp in self.return_period:
            fields.append(f"H_{rp}T{self.rainlength}_mm")
            for st in self.type:
                fields.append(f"P_{rp}tvar{st}_%")
            for st in self.type:
                fields.append(f"QAPI_tvar{st}")
        with open(ofile) as fd:
            data = DictReader(fd)
            nlines = 0
            for row in data:
                for f in fields:
                    value = float(row[f])
                    assert value >= 0
                    if f.startswith('P'):
                        assert value >= 0 and value <= 100
                    if f.startswith('QAPI'):
                        assert value >= 0 and value <= 1
                nlines += 1

            assert nlines == 15

    def test_002_d_rain6h_timedist_reduction(self):
        ofile = self._run_job(
            'd-rain6h-timedist',
            [("input", self.input_data),
             ("keycolumn", self.keycolumn),
            ] + self._request_multi("return_period") + self._request_multi("type"),
            '.csv'
        )
        self._process_d_rain6h_timedist(ofile)

    def test_003_d_rain6h_timedist_reduction_disabled(self):
        ofile = self._run_job(
            'd-rain6h-timedist',
            [("input", self.input_data),
             ("keycolumn", self.keycolumn),
             ("area_red", "false")
            ] + self._request_multi("return_period") + self._request_multi("type"),
            '.csv'
        )
        self._process_d_rain6h_timedist(ofile)

    def test_004_raintotal6h_timedist(self):
        ofile = self._run_job(
            'raintotal6h-timedist',
            [("value", self.value),
            ] + self._request_multi("type"),
            '.csv'
        )
        with open(ofile) as fd:
            data = DictReader(fd)
            time = 5
            for row in data:
                assert int(row["CAS_min"]) == time
                for st in self.type:
                    assert float(row[f"H_tvar{st}_mm"]) >= 0
                time += 5
                
    def test_005_soil_texture_hsg(self):
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

    def test_006_soil_texture_hsg20km2(self):
        ofile = self._run_job_request(
            Path(__file__).parent / 'request-soil-texture-hsg20km2.xml',
            exception="Process error: Limit 20km2 na vymeru zajmoveho uzemi prekrocen"
        )

    def test_007_rain6h_cn_runoff(self):
        ofile = self._run_job(
            'rain6h-cn-runoff',
            [("obs_x", self.obs_x),
             ("obs_y", self.obs_y),
             ("cn2", self.cn2),
             ("lambda", self.lambda_),
             ("area", self.area)] + self._request_multi("return_period"),
            '.json'
        )

        with open(ofile, 'r') as fp:
            data = json.load(fp)
            i = 0
            for rp in self.return_period:
                record = data[i]
                assert record[f"H_{rp}_T360_mm"] >= 0
                assert record[f"CN3_{rp}"] >= 0
                assert record[f"VCN2_{rp}_m3"] >= 0
                assert record[f"VCN3_{rp}_m3"] >= 0
                assert record[f"V_{rp}_m3"] >= 0
                if rp == "N100":
                    assert record[f"CN3_{rp}"] == 91
                    assert record[f"VCN2_{rp}_m3"] == 1233.82
                    assert record[f"VCN3_{rp}_m3"] == 2134.57
                    assert record[f"V_{rp}_m3"] == 1336.39

                i += 1

    def test_008_rain6h_cn_runoff101ha(self):
        self._run_job(
            'rain6h-cn-runoff',
            [("obs_x", self.obs_x),
             ("obs_y", self.obs_y),
             ("cn2", self.cn2),
             ("lambda", self.lambda_),
             ("area", "101")] + self._request_multi("return_period"),
            exception="Process error: area: outside of valid interval 0.1-100"
        )

    def test_009_rain6h_cn_runoff0(self):
        ofile = self._run_job(
            'rain6h-cn-runoff',
            [("obs_x", self.obs_x),
             ("obs_y", self.obs_y),
             ("cn2", "20"),
             ("lambda", "0.3"),
             ("area", self.area)] + self._request_multi("return_period"),
            '.json'
        )

        with open(ofile, 'r') as fp:
            data = json.load(fp)
            i = 0
            for rp in self.return_period:
                record = data[i]
                assert record[f"VCN2_{rp}_m3"] == 0
                assert record[f"VCN3_{rp}_m3"] == 0
                assert record[f"V_{rp}_m3"] == 0
                i += 1

    def test_010_smoderp2d_capabilities(self):
        processes = self._wps('https://rain1.fsv.cvut.cz:4444/services/wps').processes
        assert len(processes) == 2
        assert any(process.identifier.startswith('smoderp') for process in processes)

    def test_011_profile1d(self):
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
