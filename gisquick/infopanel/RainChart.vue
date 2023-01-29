<template>
  <div class="rain-chart">
    <div class="table">
      <label>Číslo povodí:</label>
      <span v-text="attributes.id"/>
      <label>Výměra:</label>
      <span>{{ attributes.area }} km<sup>2</sup></span>
      <label>Úhrn návrhové srážky:</label>
      <span>{{ attributes.rainfall }} mm</span>
    </div>
    <div class="title">Průběh návrhových srážek</div>
    <plot-chart
      v-if="bandsData"
      height="200"
      :bands="bands"
      :data="bandsData"
      :x-axis="xAxis"
      :y-axis="yAxis"
    >
      <template v-slot:svg-layer>
        <path
          v-for="(curve, key) in curves"
          :key="`line-${key}`"
          :class="`line data-${key}`"
          :style="colorStyles[key]"
          :d="curve"
        />
      </template>
      <template v-slot:top-overlay>
        <div class="legend my-2">
          <div
            v-for="(band, key) in bands"
            :key="key"
            class="item"
          >
            <div class="dot" :style="colorStyles[key]"/>
            <span v-text="band.label"/>
          </div>
        </div>

        <div
          class="interactive"
          @mousemove="onMouseMove"
          @mouseover="tooltipVisible = true"
          @mouseleave="tooltipVisible = false"
        >
          <div
            v-if="tooltipVisible && tooltip"
            class="tooltip"
            :class="tooltip.align"
            :style="tooltip.style"
          >
            <span class="time">{{ tooltip.time }} min.</span>
            <div class="values">
              <span
                v-for="(value, band) in tooltip.data"
                :key="band"
                :style="colorStyles[band]"
                v-text="value"
              />
            </div>
          </div>
        </div>
      </template>
    </plot-chart>
    <div class="subtitle">Zastoupení tvarů hyetogramu</div>
    <div class="bar-chart">
      <div
        v-for="(item, i) in barChart"
        :key="i"
        class="item"
        :style="item.style"
      >
        {{ formats.num1(item.value) }}%
      </div>
    </div>

    <div class="subtitle">aAPI - vztaženo k zastoupení CN2 a CN3</div>
    <div class="cn-table m-2">
      <template v-for="(data, label) in cnData">
        <span :key="label" v-text="label"/>
        <span
          v-for="(item, i) in data"
          :key="`${label}_${i}`"
          v-text="item.value"
          :style="item.style"
        />
      </template>
    </div>

    <a class="download" @click="download">Data CSV</a>
  </div>
</template>

<script>
import * as d3 from './d3-min'
import groupBy from 'lodash/groupBy'
import invert from 'lodash/invert'
import mapValues from 'lodash/mapValues'
import pick from 'lodash/pick'
import throttle from 'lodash/throttle'
import { saveAs } from 'file-saver'

import PlotChart, { bandsExtent } from './PlotChart.vue'
// import data from './rain.json'

import { getFeatureQuery, layerFeaturesQuery } from '@/map/featureinfo'

function cn2 (v) {
  if (v < 20) {
    return 1
  } else if (v < 40) {
    return 0.75
  } else if (v < 60) {
    return 0.5
  } else if (v < 80) {
    return 0.25
  } else {
    return 0
  }
}

function cn3 (v) {
  if (v < 20) {
    return 0
  } else if (v < 40) {
    return 0.25
  } else if (v < 60) {
    return 0.5
  } else if (v < 80) {
    return 0.75
  } else {
    return 1
  }
}

export default {
  name: 'RainChart',
  components: { PlotChart },
  props: {
    layer: Object,
    feature: Object,
    project: Object
  },
  data () {
    return {
      features: null, //data.features,
      tooltip: null,
      tooltipVisible: false
    }
  },
  computed: {
    formats () {
      const num1 = new Intl.NumberFormat('cs', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 1
      })
      return {
        num1: v => v && num1.format(v)
      }
    },
    hn () {
      // Navrhove_srazky-2_roky
      return this.layer.name.split('-')[1]?.split('_')[0]
    },
    rainfallAttribute () {
      return `H_N${this.hn}T360`
    },
    properties () {
      return this.feature.getProperties()
    },
    attributes () {
      return {
        id: this.properties['HLGP_CHAR'],
        area: this.properties['PLOCHA'].toFixed(2),
        rainfall: this.properties[this.rainfallAttribute]?.toFixed(1)
      }
    },
    bands () {
      return {
        A: {
          label: 'Tvar A',
          color: 'rgb(255,0,0)'
        },
        B: {
          label: 'Tvar B',
          color: 'rgb(255,124,128)'
        },
        C: {
          label: 'Tvar C',
          color: 'rgb(255,192,0)'
        },
        D: {
          label: 'Tvar D',
          color: 'rgb(25,255,0)'
        },
        E: {
          label: 'Tvar E',
          color: 'rgb(146,208,80)'
        },
        F: {
          label: 'Tvar F',
          color: 'rgb(0,112,192)'
        }
      }
    },
    colorStyles () {
      return mapValues(this.bands, g => ({ '--color': g.color }))
    },
    bandsData () {
      if (this.features) {
        return mapValues(this.features, features => features.map(f => ({
          time: parseInt(f.properties['T_(min)']),
          value: (f.properties['H5min_(%)'] / 100.0) * this.properties[this.rainfallAttribute]
        })))
      }
      return null
    },
    xAxis () {
      const w = 100
      const scale = d3.scaleLinear().range([0, w])
      scale.domain([0, 360])

      return {
        scale,
        ticks: d3.range(0, 365, 60),
        unit: 'Čas [min.]'
      }
    },
    yAxis () {
      const h = 100
      const scale = d3.scaleLinear().range([h, 0])

      const [min, max] = bandsExtent(this.bandsData, d => d.value)
      // const [min, max] = d3.extent(this.chartData, d => d.value)
      scale.domain([min, max]).nice(4)
      // scale.domain([0, 10])
      return {
        scale,
        ticks: scale.ticks(6),
        unit: '[mm]'
      }
    },
    curves () {
      if (this.bandsData) {
        const bands = Object.keys(this.bands).reverse()
        const datasets = pick(this.bandsData, bands)
        return mapValues(datasets, dataset => {
          const line = d3.line()
            .curve(d3.curveCardinal)
            .x(d => this.xAxis.scale(d.time))
            .y(d => this.yAxis.scale(d.value))
          return line(dataset)
        })
      }
    },
    barChart () {
      // const prefix = `p_n${this.hn}tvar`
      const suffix = `_00${this.hn}`
      return Object.keys(this.bands).map(type => {
        const attr = type + suffix
        const value = this.properties[attr]
        return {
          value,
          style: {
            width: Math.round(value) + '%',
            '--color': this.bands[type].color
          }
        }
      })
    },
    cnData () {
      const cnData = cn => Object.keys(this.bands).map(type => ({
        type,
        value: cn(100 * this.properties[`a06_t${type}z_1`]),
        style: { '--color': this.bands[type].color }
      }))
      return {
        CN2: cnData(cn2),
        CN3: cnData(cn3)
      }
    }
  },
  async created () {
    const features = await this.fetchData()
    this.features = features
  },
  methods: {
    async fetchData () {
      const bandLayers = mapValues(this.bands, ((v, id) => `tvar${id}`))
      const queries = Object.values(bandLayers).map(name => layerFeaturesQuery({ name }))
      const query = getFeatureQuery(queries)
      const params = {
        'VERSION': '1.1.0',
        'SERVICE': 'WFS',
        'REQUEST': 'GetFeature',
        'OUTPUTFORMAT': 'GeoJSON',
        'MAXFEATURES': 1000
      }
      const { data } = await this.$http.post(this.project.ows_url, query, { params, headers: { 'Content-Type': 'text/xml' } })
      const layersBands = invert(bandLayers)
      return groupBy(data.features, f => layersBands[f.id.split('.')[0]])
    },
    // onMouseMove (e) {
    onMouseMove: throttle(function (e) {
      const offsetX = e.layerX || e.offsetX
      const x = this.xAxis.scale.invert(100 * offsetX / e.target.clientWidth)
      const time = Math.round(x / 5) * 5
      if (this.tooltip?.time !== time) {
        this.tooltip = {
          style: {
            left: this.xAxis.scale(time) + '%'
          },
          align: time < 300 ? 'right' : 'left',
          time,
          data: mapValues(this.bandsData, dataset => dataset.find(d => d.time === time)?.value.toFixed(3))
        }
      }
    }, 50),
    download (e) {
      const types = Object.keys(this.bands)
      const header = [
        'CAS_min',
        ...types.map(t => `H_N${this.hn}tvar${t}_mm`),
        ...types.map(t => `P_N${this.hn}tvar${t}_%`),
        ...types.map(t => `CN2 ${t}`),
        ...types.map(t => `CN3 ${t}`)
      ]
      const csv = [header.join(',')]
      const firstLine = [
        0, '', '', '', '', '', '',
        ...types.map(type => this.properties[`${type}_00${this.hn}`]),
        ...this.cnData.CN2.map(i => i.value),
        ...this.cnData.CN3.map(i => i.value)
      ]
      csv.push(firstLine.join(','))
      const times = this.bandsData[types[0]].map(i => i.time)
      times.forEach((time, index) => {
        const data = [time, ...types.map(type => this.bandsData[type][index].value.toFixed(3))]
        csv.push(data.join(',') + ',,,,,,')
      })
      const blob = new Blob([csv.join('\n')], { type: 'text/plain;charset=utf-8' })
      saveAs(blob, `${this.attributes.id}_N${this.hn}.csv`)
    }
  }
}
</script>

<style lang="scss" scoped>
.rain-chart {
  display: flex;
  flex-direction: column;
  @media (min-width: 501px) {
    width: 460px;
  }
  .table {
    padding: 8px;
    display: grid;
    grid-template-columns: auto auto;
    label {
      font-weight: bold;
    }
  }
  .title {
    font-size: 18px;
    margin: 12px 8px;
    font-weight: bold;
    text-align: center;
  }
  .subtitle {
    font-size: 16px;
    margin: 8px;
    font-weight: bold;
    text-align: center;
  }
  .chart {
    padding-top: 32px;
    .line {
      fill: none;
      // stroke: currentColor;
      stroke: var(--color);
      stroke-width: 2;
      vector-effect: non-scaling-stroke;
    }
    .legend {
      position: absolute;
      top: 0;
      right: 0;
      display: flex;
      flex-direction: column;
      font-size: 12px;
      background-color: #fff;
      .item {
        display: flex;
        align-items: center;
        margin: 0 6px;
        .dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background-color: var(--color);
          flex-shrink: 0;
          margin-right: 6px;
        }
      }
    }
    .interactive {
      position: absolute;
      width: 100%;
      height: 100%;
      .tooltip {
        position: absolute;
        height: 100%;
        border-left: 1px solid #999;
        pointer-events: none;
        font-size: 13px;
        .time {
          position: absolute;
          white-space: nowrap;
          transform: translate(0, -100%);
          font-weight: bold;
        }
        .values {
          display: flex;
          flex-direction: column;
          background-color: #fcfcfc;
          border-radius: 3px;
          // border: 1px solid #ddd;
          margin: 0 3px;
          padding: 0 4px;
          box-shadow:
            0 3px 4px 0 rgba(0,0,0,.14),
            0 1px 8px 0 rgba(0,0,0,.12);
          > * {
            color: var(--color);
          }
        }
        &.left {
          .time {
            transform: translate(-100%, -100%);
          }
          .values {
            transform: translate(calc(-100% - 6px), 0);
          }
        }
      }
    }
  }
  .bar-chart {
    display: flex;
    align-items: center;
    gap: 1px;
    background-color: #444;
    border: 1px solid #444;
    border-width: 0 1px;
    height: 20px;
    font-size: 12px;
    margin: 8px;
    .item {
      background-color: var(--color);
      text-align: center;
    }
  }
  .download {
    align-self: center;
    padding: 2px 8px;
    cursor: pointer;
  }
}
.cn-table {
  display: grid;
  font-size: 14px;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: #444;
  border: 1px solid #444;
  span {
    padding: 0 4px;
    text-align: center;
    background-color: var(--color, #fff);
  }
}
</style>
