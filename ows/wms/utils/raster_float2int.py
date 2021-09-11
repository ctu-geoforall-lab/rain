# grass --tmp-location EPSG:5514 --exec python raster_float2int.py

import os
import glob
from qml2clr import qml2clr
from grass.pygrass.modules import Module

def raster_float2int(raster_float, raster_int, clr, coef=1.0):
    map_name = os.path.splitext(os.path.basename(raster_float))[0].replace('-', '_')
    Module("r.external", input=raster_float, output=map_name, flags="o")
    Module("g.region", raster=map_name)
    Module("r.mapcalc", expression=f"{map_name}_int = round({map_name} * {coef})")
    Module("r.colors", map=map_name + "_int", rules='-', stdin_=clr)
    Module("r.out.gdal", input=map_name + "_int", output=raster_int, overwrite=True)

def main(in_dir, out_dir, qml_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for inf in glob.glob(in_dir + "/*.tif"):
        fn = os.path.splitext(os.path.basename(inf))[0]
        print(f"Processing {fn}...")
        outf = os.path.join(out_dir, fn + '.tif')
        qmlf = os.path.join(qml_dir, fn + '.qml')
        
        raster_float2int(inf, outf, '\n'.join(qml2clr(qmlf)))

if __name__ == "__main__":
    main(
        "../data/soil_texture_hsg_orig",
        "../data/soil_texture_hsg",
        "../../../qgis/styles"
    )
