# grass --tmp-location EPSG:5514 --exec python3 publish_raster.py

import os
import glob
from grass.pygrass.modules import Module

from qml2clr import qml2clr
from wms_legend import create_legend

def process_raster(raster_float, raster_int, clr, is_fp, coef=1.0):
    map_name = os.path.splitext(os.path.basename(raster_float))[0]
    Module("r.import", input=raster_float, output=map_name, flags="o")
    Module("g.region", raster=map_name)
    Module("r.mapcalc", expression=f"{map_name}_int = round({map_name} * {coef})")
    Module("r.colors", map=map_name + "_int", rules='-', stdin_=clr)
    Module("r.out.gdal", input=map_name + "_int", output=raster_int, overwrite=True)
    create_legend(map_name + "_int", is_fp)

def main(in_dir, out_dir, qml_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for inf in glob.glob(in_dir + "/*.tif"):
        fn = os.path.splitext(os.path.basename(inf))[0]
        print(f"Processing {fn}...")
        outf = os.path.join(out_dir, fn + '.tif')
        if fn.startswith('H_N'):
            qmlf = os.path.join(qml_dir, fn[:3].lower() + '.qml')
        else:
            qmlf = os.path.join(qml_dir, fn + '.qml')
        clr, is_fp = qml2clr(qmlf)
        
        process_raster(inf, outf, '\n'.join(clr), is_fp)

if __name__ == "__main__":
    main(
        "../data/soil_texture_hsg_orig",
        "../data/soil_texture_hsg",
        #"../data/h_24h_orig",
        #"../data/h_24h",
        "../../../qgis/styles"
    )
