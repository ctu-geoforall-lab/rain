<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.20.0-Odense" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="1e+08">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal mode="0" fetchMode="0" enabled="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="bool" value="false" name="WMSBackgroundLayer"/>
      <Option type="bool" value="false" name="WMSPublishDataSourceUrl"/>
      <Option type="int" value="0" name="embeddedWidgets/count"/>
      <Option type="QString" value="Value" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2" zoomedOutResamplingMethod="nearestNeighbour" enabled="false"/>
    </provider>
    <rasterrenderer type="singlebandpseudocolor" band="1" nodataColor="" opacity="1" classificationMax="79.4199982" alphaBand="-1" classificationMin="2.3299999">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" maximumValue="79.419998199999995" minimumValue="2.3299998999999998" classificationMode="1" clip="0" labelPrecision="4">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" value="255,245,235,255" name="color1"/>
              <Option type="QString" value="127,39,4,255" name="color2"/>
              <Option type="QString" value="0" name="discrete"/>
              <Option type="QString" value="gradient" name="rampType"/>
              <Option type="QString" value="0.276442;254,230,206,255:0.485577;253,174,107,255:0.622596;241,105,19,255:0.807692;166,54,3,255" name="stops"/>
            </Option>
            <prop k="color1" v="255,245,235,255"/>
            <prop k="color2" v="127,39,4,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.276442;254,230,206,255:0.485577;253,174,107,255:0.622596;241,105,19,255:0.807692;166,54,3,255"/>
          </colorramp>
          <item label="2,3300" color="#fff5eb" alpha="255" value="2.3299999237061"/>
          <item label="21,6025" color="#fee7d1" alpha="255" value="21.602499485015827"/>
          <item label="40,8750" color="#fca762" alpha="255" value="40.87499904632555"/>
          <item label="60,1475" color="#bd4608" alpha="255" value="60.14749860763527"/>
          <item label="79,4200" color="#7f2704" alpha="255" value="79.419998168945"/>
          <rampLegendSettings suffix="" orientation="2" minimumLabel="" direction="0" useContinuousLegend="1" maximumLabel="" prefix="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="QChar" value="" name="decimal_separator"/>
                <Option type="int" value="6" name="decimals"/>
                <Option type="int" value="0" name="rounding_type"/>
                <Option type="bool" value="false" name="show_plus"/>
                <Option type="bool" value="true" name="show_thousand_separator"/>
                <Option type="bool" value="false" name="show_trailing_zeros"/>
                <Option type="QChar" value="" name="thousand_separator"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeGreen="128" grayscaleMode="0" colorizeRed="255" colorizeBlue="128" saturation="0" colorizeStrength="100" colorizeOn="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
