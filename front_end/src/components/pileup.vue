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
  props: {
    title: String,
    width: Number,
    height: Number,
    data: Object,
    scaleFactor: Number
  },
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
        var variables = Object.values(this.data["variable"]);
        // switch them around because otherwise plot will be mirrored
        var dataRange = new Set(variables).size;
        var reversedVars = variables.map( (element) => {
          return dataRange - element;
        })
        return reversedVars;
      }
      return null;
    },
    dataHeatMap: function() {
      return convert_json_to_d3(this.data, this.scaleFactor);
    }
  },
  data: function() {
  return {
    svg: null, // svg of heatmap,
  }
},
  methods: {
    // creates the svg object
    createHeatMap: function() {
      this.svg = d3.select(`#${this.title}`)
                   .append("svg")
                   .attr("id", `${this.title}Svg`)
                   .attr("width", this.width)
                   .attr("height", this.height)
                   .append("g")
    },
    // fills the heatmap with data
    fillHeatMap: function() {
      // Build X/Y scales and axes
      var x = d3.scaleBand()
        .range([ 0, this.width ])
        .domain(this.dataGroups)
        .padding(0.01);
      var y = d3.scaleBand()
        .range([ this.height, 0 ])
        .domain(this.dataVariables)
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
  mounted: function () {
    this.createHeatMap();
    this.fillHeatMap();
  },
  watch: {
    data: function() {
      d3.select(`#${this.title}Svg`).remove();
      this.createHeatMap();
      this.fillHeatMap();
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