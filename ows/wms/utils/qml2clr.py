#!/usr/bin/env python3

import xml.etree.ElementTree as ET

def qml2clr(qml_file, coef=1.0):
    tree = ET.parse(qml_file)
    root = tree.getroot()
    clr = []
    for node in root.findall("./pipe/rasterrenderer/rastershader/colorrampshader/item"):
        clr.append('{} {}'.format(
            round(float(node.get('value')) * coef), node.get('color')
        ))

    return clr
