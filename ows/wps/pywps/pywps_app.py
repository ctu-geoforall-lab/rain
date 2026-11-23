#!/usr/bin/env python3

__author__ = "Martin Landa"

import os
import sys
import multiprocessing
from pywps.app.Service import Service

# Python 3.14 defaults to 'forkserver' on Linux, which needs the pywps
# Process object to be picklable (it isn't: NoneIOHandler holds a weakref).
# Async execution therefore fails; restore the pre-3.14 'fork' behaviour.
multiprocessing.set_start_method('fork', force=True)

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
