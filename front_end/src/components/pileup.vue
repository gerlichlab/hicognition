<template>
  <md-card class="inner-pileup-card">
    <md-card-header>
      <div class="md-title">{{ titleName }}</div>
    </md-card-header>

    <md-card-content>
      <apexchart
        type="heatmap"
        height="350"
        :options="chartOptions"
        :series="series"
      ></apexchart>
    </md-card-content>
  </md-card>
</template>

<script>
import generateData from "../functions.js";
import VueApexCharts from 'vue-apexcharts'

export default {
  name: "pileup-card",
  props: ["title"],
  computed: {
    titleName: function () {
      if (this.title) {
        return this.title;
      }
      return "Default";
    },
  },
  components: {
    apexchart: VueApexCharts,
  },
  data: function() {
  return {
    series: [],
    chartOptions: {
      chart: {
        height: 350,
        type: "heatmap",
      },
      dataLabels: {
        enabled: false,
      },
      colors: ["#008FFB"],
      title: {
        text: "HeatMap Chart (Single color)",
      },
    },
  }
}
};
</script>

<style lang="scss" scoped>
.inner-pileup-card {
  width: 80%;
  height: 45%;
  margin: 4px;
  display: inline-block;
}
</style>

/*  [
      {
        name: "Metric1",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric2",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric3",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric4",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric5",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric6",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric7",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric8",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
      {
        name: "Metric9",
        data: generateData(18, {
          min: 0,
          max: 90,
        }),
      },
    ] */