#!/usr/bin/env python3

import xml.etree.ElementTree as ET

def qml2clr(qml_file, coef=1.0):
    tree = ET.parse(qml_file)
    root = tree.getroot()
    clr = []
    # fp
    clr_nodes = root.findall("./pipe/rasterrenderer/rastershader/colorrampshader/item")
    if not clr_nodes:
        clr_nodes = root.findall("./pipe/rasterrenderer/colorPalette/paletteEntry")

    for node in clr_nodes:
        clr.append('{} {}'.format(
            round(float(node.get('value')) * coef), node.get('color')
        ))

    return clr
