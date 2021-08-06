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
    <rasterrenderer type="singlebandpseudocolor" band="1" nodataColor="" opacity="1" classificationMax="53" alphaBand="-1" classificationMin="0.0411111">
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
        <colorrampshader colorRampType="INTERPOLATED" maximumValue="53" minimumValue="0.041111099999999998" classificationMode="1" clip="0" labelPrecision="4">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" value="233,242,247,255" name="color1"/>
              <Option type="QString" value="1,52,33,255" name="color2"/>
              <Option type="QString" value="0" name="discrete"/>
              <Option type="QString" value="gradient" name="rampType"/>
              <Option type="QString" value="0.0721154;176,221,239,255:0.235577;112,177,205,255:0.484375;23,140,152,255:0.746394;0,88,72,255" name="stops"/>
            </Option>
            <prop k="color1" v="233,242,247,255"/>
            <prop k="color2" v="1,52,33,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.0721154;176,221,239,255:0.235577;112,177,205,255:0.484375;23,140,152,255:0.746394;0,88,72,255"/>
          </colorramp>
          <item label="0,0411" color="#e9f2f7" alpha="255" value="0.041111070662737"/>
          <item label="6,9258" color="#99cde3" alpha="255" value="6.925766631476582"/>
          <item label="13,8104" color="#67adc8" alpha="255" value="13.810422192290426"/>
          <item label="20,6951" color="#399aac" alpha="255" value="20.695077753104272"/>
          <item label="27,5797" color="#14858d" alpha="255" value="27.579733313918116"/>
          <item label="34,4644" color="#086b65" alpha="255" value="34.46438887473196"/>
          <item label="41,3490" color="#005343" alpha="255" value="41.34904443554581"/>
          <item label="47,7041" color="#014230" alpha="255" value="47.704111107066275"/>
          <item label="53,0000" color="#013421" alpha="255" value="53"/>
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
