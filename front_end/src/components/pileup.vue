<template>
  <md-card class="inner-pileup-card">
    <md-card-header>
      <div class="md-title">{{ titleName }}</div>
    </md-card-header>

    <md-card-content>
      <div :id="title" />
    </md-card-content>
  </md-card>
</template>

<script>
import * as d3 from "d3";
import { iccfScale } from "../colorScales.js"
import { convert_json_to_d3 } from "../functions.js"

export default {
  name: "pileup-card",
  props: ["title", "width", "height", "data"],
  computed: {
    titleName: function () {
      if (this.title) {
        return this.title;
      }
      return "Default";
    },
    dataGroups: function () {
      if (this.data){
        return Object.values(this.data["group"])
      }
      return null;
    },
    dataVariables: function () {
      if (this.data) {
        return Object.values(this.data["variable"])
      }
      return null;
    },
    dataHeatMap: function() {
      return convert_json_to_d3(this.data);
    }
  },
  data: function() {
  return {
    svg: null, // svg of heatmap,
    margin: {top: 30, right: 30, bottom: 30, left: 30},
    svgWidth: this.width - this.margin.right - this.margin.left,
    svgHeight: this.height - this.margin.top - this.margin.bottom
  }
},
  methods: {
    // creates the svg object
    createHeatMap: function() {
      this.svg = d3.select(`#${this.title}`)
                   .append("svg")
                   .attr("width", this.width)
                   .attr("height", this.height)
                   .append("g")
                   .attr("transofrm", "translate(" + this.margin.left + "," + this.margin.top + ")");
    },
    // fills the heatmap with data
    fillHeatMap: function() {
      // Build X/Y scales and axes
      var x = d3.scaleBand()
        .range([ 0, this.width ])
        .domain(this.dataGroups)
        .padding(0.01);
      var y = d3.scaleBand()
        .range([ height, 0 ])
        .domain(myVars)
        .padding(0.01);
      this.svg.append("g").call(d3.axisBottom(x));
      this.svg.append("g").call(d3.axisLeft(y));
      // Add data
      this.svg.selectAll()
              .data(this.dataHeatMap, function(d) {return d.variable+':'+d.group;})
              .enter()
              .append("rect")
                  .attr("x", function(d) { return x(d.group) })
                  .attr("y", function(d) { return y(d.variable) })
                  .attr("width", x.bandwidth() )
                  .attr("height", y.bandwidth() )
                  .style("fill", function(d) { return iccfScale(d.value)} )
    }
  },
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