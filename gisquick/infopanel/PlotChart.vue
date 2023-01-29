<template>
  <div class="chart">
    <div class="overlay">
      <div
        v-for="(style, i) in yAxisLines"
        :key="`y-line-${i}`"
        :style="style"
        class="secondary-line y"
      />
      <div
        v-for="(style, i) in xAxisLines"
        :key="`x-line-${i}`"
        :style="style"
        class="secondary-line x"
      />
    </div>
    <svg
      ref="graph"
      class="svg-layer"
      viewBox="0 0 100 100"
      width="100%"
      :height="height"
      preserveAspectRatio="none"
    >
      <slot name="svg-layer" :chart="this"/>
    </svg>

    <div class="axis x">
      <div class="ticks">
        <div v-if="xAxisTicks.offset" :style="xAxisTicks.offset"/>
        <div
          v-for="(tick, i) in xAxisTicks.ticks"
          :key="i"
          :style="tick.style"
          class="tick"
        >
          <div class="tick-line"/>
          <span v-text="tick.label"/>
        </div>
      </div>
      <span v-if="xAxis.unit" class="unit" v-text="xAxis.unit"/>
    </div>

    <div class="axis y">
      <span v-if="yAxis.unit" class="unit" v-text="yAxis.unit"/>
      <div v-if="yAxisTicks.offset" :style="yAxisTicks.offset"/>
      <div
        v-for="(tick, i) in yAxisTicks.ticks"
        :key="i"
        :style="tick.style"
        class="tick"
      >
        <span v-text="tick.label"/>
        <div class="tick-line"/>
      </div>
    </div>

    <div class="overlay">
      <slot name="top-overlay" :chart="this"/>
    </div>
  </div>
</template>

<script>
import last from 'lodash/last'

import * as d3 from './d3-min'

function toPerc (v) {
  return Number.isInteger(v) ? v + '%' : v.toFixed(5) + '%'
}

export function bandsExtent (bands, fn) {
  const extents = Object.values(bands).map(dataset => d3.extent(dataset, fn))
  const min = d3.min(extents.map(e => e[0]))
  const max = d3.max(extents.map(e => e[1]))
  return [min, max]
}

function axisTicks (axis, sizeParam) {
  let { scale, format, ticks } = axis
  const range = scale.range()
  const domain = scale.domain()
  if (range[0] > range[1]) {
    domain.reverse()
    ticks = ticks.slice().reverse()
  }
  const [min, max] = domain
  const sPad = scale(ticks[0]) - scale(min)
  const ePad = scale(max) - scale(last(ticks))
  const sizes = []
  let prev = scale(ticks[0])
  ticks.slice(1).forEach(t => {
    const val = scale(t)
    sizes.push(val - prev)
    prev = val
  })
  sizes.push(ePad)
  const labels = format ? ticks.map(format) : ticks
  return {
    offset: sPad && { [sizeParam]: toPerc(sPad) },
    ticks: ticks.map((t, i) => ({
      style: { [sizeParam]: toPerc(sizes[i]) },
      label: labels[i]
    }))
  }
}

function axisGridLines (axis, posParam) {
  let { scale, ticks } = axis
  if (scale.domain()[0] === ticks[0]) {
    ticks = ticks.slice(1) // omit grid line on main axis position
  }
  return ticks.map(t => ({ [posParam]: toPerc(scale(t)) }))
}

export default {
  props: {
    bands: Object, // { points: Boolean, color: String, label: String }
    data: Object,
    xAxis: Object,
    yAxis: Object,
    height: [String, Number]
  },
  data () {
    return {
      tooltip: {
        value: false
      }
    }
  },
  computed: {
    xAxisTicks () {
      return axisTicks(this.xAxis, 'width')
    },
    xAxisLines () {
      return this.xAxis && axisGridLines(this.xAxis, 'left')
    },
    yAxisTicks () {
      return axisTicks(this.yAxis, 'height')
    },
    yAxisLines () {
      return this.yAxis && axisGridLines(this.yAxis, 'top')
    }
  }
}
</script>

<style lang="scss" scoped>
.svg-layer {
  grid-area: 1 / 2 / 2 / 3;
  position: relative;
  .secondary {
    fill: none;
    stroke-width: 1;
    stroke: #ccc;
    stroke-dasharray: 5 5;
    vector-effect: non-scaling-stroke;
  }
}
.chart {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: 1fr auto;
  padding: 8px 20px 8px 8px;
  overflow: hidden;
  .axis {
    display: flex;
    font-size: 13px;
    position: relative;
    font-weight: bold;
    &.x {
      grid-area: 2 / 2 / 3 / 3;
      flex-direction: column;
      .ticks {
        display: flex;
        border-top: 1px solid #999;
        .tick {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          span {
            padding: 4px 0;
            transform: translate(-50%, 0);
          }
          .tick-line {
            height: 4px;
            width: 1px;
            background-color: #999;
          }
        }
      }
      .unit {
        align-self: center;
      }
    }

    &.y {
      grid-area: 1 / 1 / 2 / 2;
      border-right: 1px solid #999;
      flex-direction: column;
      align-items: flex-end;
      margin-right: -1px;
      .unit {
        height: 0;
        transform: translate(0, -24px);
        padding-right: 6px;
      }
      .tick {
        display: flex;
        align-items: flex-start;
        span {
          flex-grow: 1;
          transform: translate(0, -50%);
          padding-right: 6px;
        }
        .tick-line {
          width: 3px;
          height: 1px;
          background-color: #999;
        }
      }
    }
  }
  .overlay {
    grid-area: 1 / 2 / 2 / 3;
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    bottom: 0;
    // background-color: rgba(0,0,0,0.03);
    .secondary-line {
      position: absolute;
      &.y {
        left: 0;
        right: 0;
        border-bottom: 1px dashed #ddd;
      }
      &.x {
        top: 0;
        bottom: 0;
        border-right: 1px dashed #ddd;
      }
    }
  }
}
</style>
