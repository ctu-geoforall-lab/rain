#!/usr/bin/env python3

import os
from grass.pygrass.modules import Module

def create_legend(rast, is_fp, output_dir='../legend'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    Module('g.region', raster=rast)
    Module('d.mon', start='cairo', width=71, height=258,
            output=os.path.join(output_dir, rast.replace("_int", "") + '.png'),
            overwrite=True)
    Module('d.legend', raster=rast, at=[10,90,10,50],
           flags="sf" if is_fp else "f")
    Module('d.mon', stop='cairo')
