<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" maxScale="0" version="3.20.0-Odense" minScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" mode="0" fetchMode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="false" name="WMSBackgroundLayer" type="bool"/>
      <Option value="false" name="WMSPublishDataSourceUrl" type="bool"/>
      <Option value="0" name="embeddedWidgets/count" type="int"/>
      <Option value="Value" name="identify/format" type="QString"/>
    </Option>
  </customproperties>
  <pipe>
    <provider>
      <resampling enabled="false" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" alphaBand="-1" type="paletted" band="1" opacity="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry value="0" color="#3fea95" label="NoData" alpha="0"/>
        <paletteEntry value="1" color="#215968" label="clay" alpha="255"/>
        <paletteEntry value="2" color="#378975" label="silty clay" alpha="255"/>
        <paletteEntry value="3" color="#92809e" label="silty clay loam" alpha="255"/>
        <paletteEntry value="4" color="#823e50" label="clay loam" alpha="255"/>
        <paletteEntry value="5" color="#f28730" label="silt" alpha="255"/>
        <paletteEntry value="6" color="#996633" label="silty loam" alpha="255"/>
        <paletteEntry value="7" color="#92b548" label="sandy clay" alpha="255"/>
        <paletteEntry value="8" color="#663300" label="loam" alpha="255"/>
        <paletteEntry value="9" color="#a6b787" label="sandy clay loam" alpha="255"/>
        <paletteEntry value="10" color="#f0be50" label="sandy loam" alpha="255"/>
        <paletteEntry value="11" color="#efe11b" label="loamy sand" alpha="255"/>
        <paletteEntry value="12" color="#ffff00" label="sand" alpha="255"/>
      </colorPalette>
      <colorramp name="[source]" type="randomcolors">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast gamma="1" contrast="0" brightness="0"/>
    <huesaturation colorizeRed="255" colorizeGreen="128" saturation="0" colorizeStrength="100" grayscaleMode="0" colorizeOn="0" colorizeBlue="128"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
