#!/usr/bin/env python3

__author__ = "Martin Landa"

import os
import sys
from pywps.app.Service import Service

os.environ['GISBASE'] = '/usr/lib/grass84'
sys.path.append(os.path.join(os.environ["GISBASE"], "etc", "python"))

from processes.d_rain6h_timedist import DRain6hTimedist
from processes.raintotal6h_timedist import Raintotal6hTimedist
from processes.soil_texture_hsg import SoilTextureHsg
from processes.rain6h_cn_runoff import Rain6hCnRunoff

processes = [
    DRain6hTimedist(),
    Raintotal6hTimedist(),
    SoilTextureHsg(),
    Rain6hCnRunoff()
]

application = Service(
    processes,
    ['/opt/pywps/pywps.cfg']
)
