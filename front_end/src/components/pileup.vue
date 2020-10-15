<template>

  <div>
    <md-list class="md-double-line">
      <md-subheader>{{ title }}</md-subheader>
      <md-list-item class="md-alignment-top-center">
        <md-content class="center-horizontal md-elevation-3">
          <div :id="pileupDivID" class="small-margin" />
        </md-content>
      </md-list-item>
      <md-list-item>
        <doubleRangeSlider @slider-change="handleSliderChange" :sliderMin="sliderMin" :sliderMax="sliderMax"/>
      </md-list-item>
    </md-list>
  </div>

</template>

<script>
import * as d3 from "d3";
import { getScale } from "../colorScales.js"
import { convert_json_to_d3 } from "../functions.js"
import doubleRangeSlider from "./doubleRangeSlider"

export default {
  name: "pileup-card",
  props: {
    title: String,
    pileupData: Object,
    width: Number,
    height: Number,
    scaleFactor: Number,
    pileupType: String,
    pileupID: String,
    sliderMin: String,
    sliderMax: String,
    log: String
  },
  components: {
    doubleRangeSlider
  },
  computed: {
    logValue: function () {
      return Boolean(this.log);
    },
    pileupDivID: function () {
      // ID for the div containing the pileup
      return this.pileupType + this.pileupID;
    },
    titleName: function () {
      if (this.title) {
        return this.title;
      }
      return "Default";
    },
    dataGroups: function () {
      if (this.pileupData){
        return Object.values(this.pileupData["group"])
      }
      return null;
    },
    dataVariables: function () {
      if (this.pileupData) {
        var variables = Object.values(this.pileupData["variable"]);
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
      return convert_json_to_d3(this.pileupData, this.scaleFactor, this.logValue);
    },
    svgWidth: function () {
      return this.width - this.margin.left - this.margin.right
    },
    svgHeight: function () {
      return this.height - this.margin.top - this.margin.bottom
    }
  },
  data: function() {
  return {
    svg: null, // svg of heatmap,
    pileupPicture: null, // heatmap object
    colorScale: null,
    margin: {top: 0, right: 0, bottom: 0, left: 0}
  }
},
  methods: {
    handleSliderChange: function(value) {
      var min = Number(value[0]);
      var max = Number(value[1]);
      this.updateColorScale(min, max);
    },
    updateColorScale: function (min, max) {
      this.colorScale = getScale(min, max, this.pileupType);
    },
    // creates the svg object
    createHeatMap: function() {
      this.svg = d3.select(`#${this.pileupDivID}`)
                   .append("svg")
                   .attr("id", `${this.pileupDivID}Svg`)
                   .attr("width", this.width)
                   .attr("height", this.height)
                   .attr("style", "transform: translateY(2%);") // center element vertically
    },
    // fills the heatmap with data
    fillHeatMap: function() {
      // Build X/Y scales and axes
      var x = d3.scaleBand()
        .range([ 0, this.svgWidth ])
        .domain(this.dataGroups)
        .padding(0.01);
      var y = d3.scaleBand()
        .range([ this.svgHeight, 0 ])
        .domain(this.dataVariables)
        .padding(0.01);
/*       this.svg.append("g")
              .attr("transform", "translate(0," + this.svgHeight + ")")
              .call(d3.axisBottom(x)); */
/*       this.svg.append("g").call(d3.axisLeft(y)); */
      // Add data
      this.pileupPicture = this.svg.selectAll()
                                  .data(this.dataHeatMap, function(d) {return d.variable+':'+d.group;})
                                  .enter()
                                  .append("rect")
                                      .attr("x", function(d) { return x(d.group) })
                                      .attr("y", function(d) { return y(d.variable) })
                                      .attr("width", x.bandwidth() )
                                      .attr("height", y.bandwidth() )
                                      .style("fill", (d) => {
                                          if (d.value){
                                            return this.colorScale(d.value);
                                          }else{
                                            return "#ffffff";
                                          }
                                        })
    }
  },
  mounted: function () {
    this.updateColorScale(this.sliderMin, this.sliderMax); //initial range
    this.createHeatMap();
    this.fillHeatMap();
  },
  watch: {
    pileupData: function() {
      d3.select(`#${this.pileupDivID}Svg`).remove();
      this.createHeatMap();
      this.fillHeatMap();
    },
    colorScale: function () {
      // update plot
      if (this.pileupPicture) {
        this.pileupPicture.style("fill", (d) => { return this.colorScale(d.value)} )
      }

    }
  }
};
</script>

<style lang="scss" scoped>

.center-horizontal {
  margin: auto;
  display: block;
}

.small-margin {
  margin: 5px;
}

</style>