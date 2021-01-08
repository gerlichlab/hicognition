<template>
  <div>
    <md-list class="md-double-line">
      <md-list-item class="md-alignment-top-center">
        <!-- Pileup display -->
        <md-content class="center-horizontal md-elevation-1">
          <div :id="pileupDivID" class="small-margin" />
        </md-content>
      </md-list-item>
      <!-- Slider -->
<!--       <md-list-item>
        <doubleRangeSlider
          @slider-change="handleSliderChange"
          :sliderMin="sliderMin"
          :sliderMax="sliderMax"
          :sliderWidth="width"
        />
      </md-list-item> -->
    </md-list>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getScale } from "../colorScales.js";
import { convert_json_to_d3 } from "../functions.js";
import doubleRangeSlider from "./doubleRangeSlider";

export default {
  name: "pileup",
  props: {
    title: String,
    pileupData: Object,
    width: Number,
    height: Number,
    pileupType: String,
    pileupID: Number, // pileup ID is needed because I am accessing the div of the pileup via id and they must be different for different pilups
    log: Boolean,
  },
  components: {
    doubleRangeSlider,
  },
  computed: {
    pileupDivID: function () {
      // ID for the div containing the pileup
      return "pileup_" + this.pileupID;
    },
    dataGroups: function () {
      // Nomenclature: groups is first column of tidy data
      if (this.pileupData) {
        // this.pleupData["group"] is an object of the form { index0: value0, index1: value1, ... }
        return Object.values(this.pileupData["group"]);
      }
      return null;
    },
    dataVariables: function () {
      // Nomenclature: variables is second column of tidy data
      if (this.pileupData) {
        // this.pleupData["variable"] is an object of the form { index0: value0, index1: value1, ... }
        var variables = Object.values(this.pileupData["variable"]);
        // switch them around because otherwise plot will be mirrored
        var dataRange = new Set(variables).size - 1;
        var reversedVars = variables.map((element) => {
          return dataRange - element;
        });
        return reversedVars;
      }
      return null;
    },
    sliderMin: function () {
      // minimum value for heatmap lookuptable = minimum value in data
      // filter out nans and extract values into array
      var heatMapValues = this.dataHeatMap
        .filter( element => element.value)
        .map( element => element.value);
      return Math.min(...heatMapValues);
    },
    sliderMax: function () {
      // maximum value for heatmap lookuptable = maximum value in data
      // filter out nans and extract values into array
      var heatMapValues = this.dataHeatMap
        .filter( element => element.value)
        .map( element => element.value);
      return Math.max(...heatMapValues);
    },
    dataHeatMap: function () {
      // data preparation for d3
      return convert_json_to_d3(this.pileupData, this.log);
    }
  },
  data: function () {
    return {
      svg: null, // svg of heatmap,
      pileupPicture: null, // heatmap object
      colorScale: null
    };
  },
  methods: {
    redrawHeatMap: function () {
      d3.select(`#${this.pileupDivID}Svg`).remove();
      // blank picture to avoid triggering update in colorScale watcher
      this.pileupPicture = null;
      this.updateColorScale(this.sliderMin, this.sliderMax); //initial range
      this.createHeatMap();
      this.fillHeatMap();
    },
    handleSliderChange: function (value) {
      var min = Number(value[0]);
      var max = Number(value[1]);
      this.updateColorScale(min, max);
    },
    updateColorScale: function (min, max) {
      this.colorScale = getScale(min, max, this.pileupType);
    },
    createHeatMap: function () {
      // creates the svg object
      this.svg = d3
        .select(`#${this.pileupDivID}`)
        .append("svg")
        .attr("id", `${this.pileupDivID}Svg`)
        .attr("width", this.width)
        .attr("height", this.height)
        .attr("style", "transform: translateY(1%);"); // center element vertically
    },
    fillHeatMap: function () {
      // fills the heatmap with data
      // Build X/Y scales and axes
      var x = d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.dataGroups)
        .padding(0.01);
      var y = d3
        .scaleBand()
        .range([this.height, 0])
        .domain(this.dataVariables)
        .padding(0.01);
      // TODO: make axes look nice!
      this.pileupPicture = this.svg
        .selectAll()
        .data(this.dataHeatMap, function (d) {
          return d.variable + ":" + d.group;
        })
        .enter()
        .append("rect")
        .attr("x", function (d) {
          return x(d.group);
        })
        .attr("y", function (d) {
          return y(d.variable);
        })
        .attr("width", x.bandwidth())
        .attr("height", y.bandwidth())
        .style("fill", (d) => {
          if (d.value) {
            return this.colorScale(d.value);
          } else {
            return "#ffffff";
          }
        });
    },
  },
  mounted: function () {
    this.updateColorScale(this.sliderMin, this.sliderMax); //initial range
    this.createHeatMap();
    this.fillHeatMap();
  },
  watch: {
    height: function () {
      this.redrawHeatMap();
    },
    width: function () {
      this.redrawHeatMap();
    },
    pileupData: function () {
      this.redrawHeatMap();
    },
    colorScale: function () {
      // update plot with new color scale
      if (this.pileupPicture) {
        this.pileupPicture.style("fill", (d) => {
          return this.colorScale(d.value);
        });
      }
    },
  },
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