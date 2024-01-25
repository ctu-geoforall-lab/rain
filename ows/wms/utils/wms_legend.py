#!/usr/bin/env python3

import os
from grass.pygrass.modules import Module

def create_legend(rast, is_fp, output_dir='../legend', size=(71, 258)):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    Module('g.region', raster=rast)
    Module('d.mon', start='cairo', width=size[0], height=size[1],
            output=os.path.join(output_dir, rast.replace("_int", "") + '.png'),
            overwrite=True)
    Module('d.legend', raster=rast, at=[10,90,10,50],
           flags="sf" if is_fp else "", font="DejaVuSans")
    Module('d.mon', stop='cairo')

if __name__ == "__main__":
    import sys
    # usda 250x358
    # hsg 150x200
    create_legend(sys.argv[1], False, size=(sys.argv[2], sys.argv[3]))
