#!/usr/bin/env python3

__author__ = "Martin Landa"

import os
import sys
from pywps.app.Service import Service

os.environ['GISBASE'] = '/usr/lib/grass78' 
sys.path.append(os.path.join(os.environ["GISBASE"], "etc", "python"))

from processes.subdayprecip_design_shapes import SubDayPrecipShapes
from processes.subdayprecip_design_shapes_total import SubDayPrecipShapesTotal
from processes.soil_texture_hsg import SoilTextureHsgProcess
from processses.cn_rain6h import CnRain6h

processes = [
    SubDayPrecipShapes(),
    SubDayPrecipShapesTotal(),
    SoilTextureHsgProcess(),
    CnRain6h()
]

application = Service(
    processes,
    ['/opt/pywps/pywps.cfg']
)
