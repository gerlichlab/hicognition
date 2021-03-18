<template>
  <div>
    <md-list class="md-double-line">
      <md-list-item class="md-alignment-top-center">
        <!-- Stackup display -->
        <md-content class="center-horizontal md-elevation-1">
          <div :id="stackupDivID" class="canvas small-margin" :style="canvasStyle" />
        </md-content>
      </md-list-item>
    </md-list>
  </div>
</template>

<script>
import * as d3 from "d3";
import { createMatrixRenderer, createLibrary } from "piling.js"
import { convert_json_to_pilingJS } from "../functions.js";
import { createColorMap } from "../colorScales"


export default {
  name: "stackup",
  props: {
    stackupData: Object,
    width: Number,
    height: Number,
    stackupType: String,
    stackupID: Number, // stackup ID is needed because I am accessing the div of the stackup via id and they must be different for different pilups
    log: Boolean,
  },
  computed: {
    stackupDivID: function () {
      // ID for the div containing the stackup
      return "stackup_" + this.stackupID;
    },
    sliderMin: function () {
      // minimum value for heatmap lookuptable = minimum value in data
      // filter out nans and extract values into array
      var heatMapValues = this.dataHeatMapPiling[0]["src"]["data"]
        .filter( element => element);
      return Math.min(...heatMapValues);
    },
    sliderMax: function () {
      // maximum value for heatmap lookuptable = maximum value in data
      // filter out nans and extract values into array
      var heatMapValues = this.dataHeatMapPiling[0]["src"]["data"]
        .filter( element => element);
      return Math.max(...heatMapValues);
    },
    dataHeatMapPiling: function() {
      return convert_json_to_pilingJS(this.stackupData, this.log);
    }
  },
  data: function () {
    return {
      colorMap: undefined,
      matrixRenderer: undefined,
      piling: undefined,
      canvasStyle: {
        height: `${this.height}px`,
        width: `${this.width}px`
      }
    };
  },
  methods: {
    initPiling: function(domElementID, renderer, data) {
          this.piling = createLibrary(
              document.getElementById(domElementID),
              {
                  renderer: renderer,
                  items: data,
                  itemSize: this.width,
                  previewPadding: 0,
                  cellPadding: 0
              }
          )
      },
    initMatrixRenderer: function(properties) {
          this.matrixRenderer = createMatrixRenderer(properties)
    },
    initColormap: function(colorMapType) {
         this.colorMap = createColorMap(colorMapType)
      },
    changeData: function() {
      this.initColormap(this.stackupType);
      var properties = {
          colorMap: this.colorMap,
          domain: [this.sliderMin, this.sliderMax]
      }
      this.initMatrixRenderer(properties);
      this.piling.set("items", this.dataHeatMapPiling);
      this.piling.set("renderer", this.matrixRenderer);
      this.piling.render();
    },
  },
  mounted: function () {
      this.initColormap(this.stackupType);
      var properties = {
          colorMap: this.colorMap,
          domain: [this.sliderMin, this.sliderMax]
      }
      this.initMatrixRenderer(properties);
      this.initPiling(this.stackupDivID, this.matrixRenderer, this.dataHeatMapPiling)
  },
  beforeDestroy: function() {
        // destroy piling
        this.piling.destroy()
  },
  watch: {
    stackupData: function () {
      this.changeData()
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

.canvas {
    pointer-events: none;
    display: block;
    overflow: hidden;
    position: relative;
}

</style>