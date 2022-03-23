<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center" v-show="!allNull">
                <!-- this prevents drag events to allow slider change without causing widget drag -->
                <div
                    :style="colorBarContainerStyle"
                    draggable="true"
                    @dragstart.prevent.stop
                >
                    <color-bar-slider
                        :colormap="colormap"
                        :sliderMin="minValue"
                        :sliderMax="maxValue"
                        :heatMapWidth="width"
                        :sliderPositionMax="maxValueRobust"
                        :sliderPositionMin="minValueRobust"
                        :borderColor="valueScaleColor"
                        :borderStyle="valueScaleBorder"
                        :allowValueScaleChange="allowValueScaleChange"
                        @slider-change="handleColorChange"
                    >
                    </color-bar-slider>
                </div>
                <!-- Pileup display -->
                <md-content class="center-horizontal md-elevation-4" ref="contentDiv">
                        <div :class="heatmapClass"  ref="canvasDiv" @mouseleave="handleMouseLeaveContainer"/>
                        <div v-if="showXaxis" class="small-margin-left-right" :id="xAxisdivID"/>
                </md-content>
            </md-list-item>
            <div v-show="allNull">
                <md-empty-state
                    md-icon="info"
                    md-label="No data for this condition"
                    :style="emptyStyle"
                >
            </md-empty-state>
        </div>
        </md-list>
    </div>
</template>
<script>
import * as PIXI from "pixi.js-legacy";
import * as d3 from "d3";
import { getScale } from "../../colorScales.js";
import colorBarSlider from "../ui/colorBarSlider.vue";
import { getPercentile, getPerMilRank } from "../../functions";
import {formattingMixin} from "../../mixins"


// set pixi scale mode

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result.slice(1, 4).map(el => parseInt(el, 16));
}

const EXPANSION_FACTOR = 0.2
const COLORBAR_FRACTION = 0.17

export default {
    name: "heatmap",
    components: {
        colorBarSlider
    },
    mixins: [formattingMixin],
    props: {
        title: String,
        stackupData: Object,
        width: Number,
        height: Number,
        stackupID: Number,
        minHeatmapRange: Number, // min Value for heatmap range
        maxHeatmapRange: Number, // max Value for heatmap range
        minHeatmapValue: Number, // minPosition in heatmap
        maxHeatmapValue: Number, // maxPosition in heatmap
        colormap: String,
        valueScaleColor: String,
        valueScaleBorder: String,
        allowValueScaleChange: Boolean,
        windowsize: String,
        log: Boolean,
        showXaxis: {
            type: Boolean,
            default: false
        },
        isInterval: { //  whehter to show interval start and end on x axis
            type: Boolean,
            default: false
        }

    },
    computed: {
        heatmapClass: function(){
            if (this.isInterval){
                return "small-margin-left-right-top"
            }
            return "small-margin"
        },
        emptyStyle: function(){
            return {
                "padding": "0px",
                "width": this.width + "px",
                "height": this.height + "px",
            }
        },
        xAxismargin: function() {
            return {
                top: 0,
                bottom: 0,
                left: 0,
                right: 0
            }
        },
        xAxisHeight: function(){
            return (this.height * 0.07) - this.xAxismargin.bottom - this.xAxismargin.top
        },
        xAxisWidth: function(){
            return this.visualizationSize - this.xAxismargin.left - this.xAxismargin.right
        },
        heatMapHeight: function(){
            return (this.height * 0.93) - 7
        },
        xAxisdivID: function() {
            // ID for the div containing the lineprofile
            return "xAxis_" + this.id;
        },
        xAxisFontSize: function(){
            let fontSize = 10 + Math.round(this.width/50) - 2
            return `${fontSize}px`
        },
        intervalStartBin: function(){
            if (this.stackupData) {
                let intervalSize = Math.round(this.stackupData.shape[1]/ (1 + 2*EXPANSION_FACTOR))
                return Math.round(intervalSize * EXPANSION_FACTOR)
            }
            return undefined
        },
        intervalEndBin: function(){
            if (this.stackupData) {
                let intervalSize = Math.round(this.stackupData.shape[1]/ (1 + 2*EXPANSION_FACTOR))
                return intervalSize + Math.round(intervalSize * EXPANSION_FACTOR)
            }
            return undefined
        },
        nan_color: function(){
            return [255, 255, 255]
        },
        visualizationSize: function() {
            return Math.floor(Math.min(this.width, this.heatMapHeight));
        },
        colorBarContainerStyle: function() {
            return {
                width: `${COLORBAR_FRACTION * 100}%`,
                height: this.height + "px",
                display: "inline"
            };
        },
        sliderContainerStyle: function() {
            return {
                width: "100%",
                margin: "0 auto",
                height: this.sliderHeight + "px",
                display: "flex",
                "justify-content": "center",
                "align-content": "center"
            };
        },
        stackupValues: function() {
            /*
                applies log if defined
            */
            if (this.log) {
                return this.stackupData["data"].map(val => {
                    if (val && val > 0) {
                        return Math.log2(val);
                    }
                    return null;
                });
            }
            return this.stackupData["data"];
        },
        stackupDimensions: function() {
            return this.stackupData["shape"];
        },
        stackupDtype: function() {
            return this.stackupData["dtype"];
        },
        minValueRobust: function() {
            if (this.minHeatmapValue) {
                return this.minHeatmapValue;
            }
            return getPercentile(this.stackupValues, 1);
        },
        maxValueRobust: function() {
            if (this.maxHeatmapValue) {
                return this.maxHeatmapValue;
            }
            return getPercentile(this.stackupValues, 99);
        },
        minValue: function() {
            // find minimum by hand because Math.min cannot handle more than
            // a few k elements...
            if (this.minHeatmapRange) {
                return this.minHeatmapRange;
            }
            return getPerMilRank(this.stackupValues, 1);
        },
        maxValue: function() {
            // maximum value for heatmap lookuptable = maximum value in data
            // filter out nans and extract values into array
            if (this.maxHeatmapRange) {
                return this.maxHeatmapRange;
            }
            return getPerMilRank(this.stackupValues, 999);
        },
        rgbArray: function() {
            // array with rgba values for pixi Texture.fromBuffer
            var bufferArray = [];
            let allNull = true;
            for (var element of this.stackupValues) {
                // convert data into rgb values
                var colorValues;
                if (element) {
                    // indicate that not all values are nan
                    allNull = false
                    if (this.colorScale(element)[0] == "#") {
                        colorValues = hexToRgb(this.colorScale(element));
                    } else {
                        colorValues = this.colorScale(element)
                            .split(/[\,,(,)]/)
                            .slice(1, 4)
                            .map(element => Number(element));
                    }
                } else {
                    colorValues = this.nan_color;
                }
                // add to bufferarray
                for (var value of colorValues) {
                    bufferArray.push(value);
                }
                // add full saturation
                bufferArray.push(255);
            }
            this.allNull = allNull
            return new Uint8ClampedArray(bufferArray);
        }
    },
    data: function() {
        return {
            renderer: undefined,
            stage: undefined,
            texture: undefined,
            sprite: undefined,
            colorScale: undefined,
            imageData: undefined,
            id: Math.round(Math.random() * 1000000),
            pseudoCanvasContext: undefined,
            pseudoCanvas: undefined,
            allNull: false,
            trackMouse: false,
            xScale: undefined
        };
    },
    methods: {
        createXaxisScales: function() {
            this.xScale = d3
                .scaleLinear()
                .domain([0, this.stackupData.shape[1]])
                .range([0, this.xAxisWidth]);
        },
        createXaxisSvg: function() {
            d3.select(`#${this.xAxisdivID}Svg`).remove();
            this.svg = d3
                .select(`#${this.xAxisdivID}`)
                .append("svg")
                .attr("id", `${this.xAxisdivID}Svg`)
                .attr(
                    "width",
                    this.xAxisWidth
                )
                .attr(
                    "height",
                    this.xAxisHeight
                )
                .append("g")
                .attr(
                    "transform",
                    "translate(" +
                        this.xAxismargin.left +
                        "," +
                        this.xAxismargin.top +
                        ")"
                );
        },
        xAxisGenerator: function(args){
            if (this.isInterval) {
                return d3
                    .axisBottom(this.xScale)
                    .tickFormat(val => this.getXaxisFormatInterval(val))
                    .tickSizeOuter(0)
                    .tickValues([this.intervalStartBin, this.intervalEndBin])(args); 
            } else {
                // get start and end bin
                let startOffsetBp = Math.round(this.windowsize * EXPANSION_FACTOR)
                let binsize = Math.round(2 * this.windowsize / this.stackupDimensions[1])
                let startBin = Math.round(startOffsetBp/binsize)
                let endBin = this.stackupDimensions[1] - startBin
                return d3
                    .axisBottom(this.xScale)
                    .tickFormat(val => this.getXaxisFormatPoint(val))
                    .tickSizeOuter(0)
                    .tickValues([startBin, Math.round(this.stackupDimensions[1]/2), endBin])(args);    
            }
        },
        getXaxisFormatInterval: function(val){
            if (val == this.intervalStartBin){
                return "Start"
            }
            if (val == this.intervalEndBin){
                return "End"
            }
            return undefined
        },
        getXaxisFormatPoint: function(val){
            // get start and end bin
            let startOffsetBp = Math.round(this.windowsize * EXPANSION_FACTOR)
            let binsize = Math.round( 2*this.windowsize / this.stackupDimensions[1])
            let startBin = Math.round(startOffsetBp/binsize)
            let endBin = this.stackupDimensions[1] - startBin
            let tickIndicator = Number(this.windowsize) - (Math.round(Number(this.windowsize)) * EXPANSION_FACTOR)
            if (val == startBin){
                return `-${this.convertBasePairsToReadable(tickIndicator)}`
            }
            if (val == Math.round(this.stackupDimensions[1]/2)){
                return "0"
            }
            if (val == endBin){
                return `+${this.convertBasePairsToReadable(tickIndicator)}`
            }
            return undefined
        },
        createAxes: function() {
            this.svg
            .append("g")
            .attr("class", "x axis")
            .call(this.xAxisGenerator);
            this.svg.selectAll("text").style("font-size", this.xAxisFontSize);
            this.svg.selectAll('.tick')
                      .style('stroke-width','3px');
            this.svg.selectAll(".domain").style("opacity", 0)
        },
        createRenderer: function() {
            this.renderer = new PIXI.CanvasRenderer({
                width: this.visualizationSize,
                height: this.visualizationSize
            });
        },
        destroyPseudoCanvas: function() {
            if (this.pseudoCanvas) {
                this.pseudoCanvas.remove();
            }
        },
        createPseudoCanvas: function() {
            let canvas = document.createElement("canvas");
            canvas.id = `pseudoCanvas${this.id}`;
            canvas.width = this.stackupDimensions[1];
            canvas.height = this.stackupDimensions[0];
            canvas.style.top = "50px";
            canvas.style.left = `-${this.width + 200}px`;
            canvas.style.position = "absolute";
            document.body.appendChild(canvas);
            // store cnavas
            this.pseudoCanvas = canvas;
            // get canvas2d context
            this.pseudoCanvasContext = canvas.getContext("2d");
        },
        handleColorChange: function(data) {
            let concatenatedValues = data.concat([
                this.minValue,
                this.maxValue
            ]);
            this.$emit("slider-change", concatenatedValues); // propagate up to store in store
            this.createColorMap(...data);
            this.drawHeatmap();
        },
        createColorMap: function(minVal, maxVal) {
            this.colorScale = getScale(minVal, maxVal, this.colormap);
        },
        resizeCanvas: function(width, height) {
            this.renderer.resize(width, height);
        },
        getMouseCoordinates: function(mousedata) {
            let contentDiv =  this.$refs["contentDiv"].$el
            let style = window.getComputedStyle(contentDiv)
            let marginLeft = Number(style.marginLeft.split("px")[0])
            let marginTop = Number(style.marginTop.split("px")[0])
            let adjustedX = this.width * COLORBAR_FRACTION + mousedata.data.global.x + marginLeft // 16 is padding
            let adjustedY = 14.5 + mousedata.data.global.y + marginTop // 14.5 is accumulated top margins
            return [mousedata.data.global.x, mousedata.data.global.y, adjustedX, adjustedY]
        },
        hanldeMouseClick: function(mousedata) {
            // get margin of content -> this is dynamic
            let [x, y, adjustedX, adjustedY] = this.getMouseCoordinates(mousedata)
            this.$emit("heatmap-clicked", x, y, adjustedX, adjustedY)
        },
        handleMouseMove: function(mousedata) {
            if (this.trackMouse) {
                // get margin of content -> this is dynamic
                let [x, y, adjustedX, adjustedY] = this.getMouseCoordinates(mousedata)
                this.$emit("mouse-move",  x, y, adjustedX, adjustedY, this.visualizationSize)
            }
        },
        throttleFunction: function (func, delay) {
            let timerId;
            return function(mousedata) {
                if (timerId) {
                    return
                }
                // Schedule a setTimeout after delay seconds
                timerId  =  setTimeout(function () {
                    func(mousedata)
                    
                    // Once setTimeout function execution is finished, timerId = undefined so that in <br>
                    // the next scroll event function execution can be scheduled by the setTimeout
                    timerId  =  undefined;
                }, delay)
            }
        },
        handleMouseOver: function(mousedata){
            this.trackMouse = true
            let [x, y, adjustedX, adjustedY] = this.getMouseCoordinates(mousedata)
            this.$emit("mouse-enter", x, y, adjustedX, adjustedY)
        },
        handleMouseOut: function(mousedata){
            this.trackMouse = false
            this.$emit("mouse-leave")
        },
        handleMouseLeaveContainer: function() {
            // triggers when mouse leaves the heatmap container
            this.trackMouse = false
            this.$emit("mouse-leave-container")
        },
        drawHeatmap: function() {
            // destroy old pseudocanvas if existing
            this.destroyPseudoCanvas();
            this.createPseudoCanvas();
            this.imageData = new ImageData(
                this.rgbArray,
                this.stackupDimensions[1],
                this.stackupDimensions[0]
            );
            // add image to pseudocanvas
            this.pseudoCanvasContext.putImageData(this.imageData, 0, 0);
            // create texture form pseudocanvas
            this.texture = PIXI.Texture.from(this.pseudoCanvas);
            this.sprite = PIXI.Sprite.from(this.texture);
            //  attach event handlers
            let scalingFactor = this.stackupDimensions[0]/this.stackupDimensions[1]
            this.sprite.hitArea = new PIXI.Rectangle(0, 0 , this.visualizationSize, this.visualizationSize * scalingFactor )
            this.sprite.click = this.hanldeMouseClick
            this.sprite.pointermove = this.throttleFunction(this.handleMouseMove, 50)
            this.sprite.mouseover = this.handleMouseOver
            this.sprite.mouseout = this.handleMouseOut
            this.sprite.interactive = true
            // position sprite at top left and make it stretch the canvas
            this.sprite.x = 0;
            this.sprite.y = 0;
            this.sprite.width = this.visualizationSize;
            this.sprite.height = this.visualizationSize;
            // add and render
            this.stage.addChild(this.sprite);
            this.renderer.render(this.stage);
            // add hit area

            this.renderer.render(this.stage)
            // add x Axis if necessary
            if (this.showXaxis){
                this.createXaxisScales()
                this.createXaxisSvg()
                this.createAxes()
            }
        },
        initializeCanvas: function() {
            // add the renderer view object into the canvas div
            this.$refs["canvasDiv"].appendChild(this.renderer.view);
            // create stage
            this.stage = new PIXI.Container();
        }
    },
    watch: {
        stackupData: function() {
            // rerender if stackupdata changes -> important for sorting
            if (this.minHeatmapValue && this.maxHeatmapValue) {
                this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
            } else {
                this.createColorMap(this.minValueRobust, this.maxValueRobust);
                // emit slider change to set initial values in pileupWidget
                this.$emit("slider-change", [
                    this.minValueRobust,
                    this.maxValueRobust,
                    this.minValue,
                    this.maxValue
                ]);
            }
            this.drawHeatmap();
        },
        isInterval: function(oldVal, newVal) {
            if (oldVal != newVal) {
                this.$refs["canvasDiv"].removeChild(this.renderer.view);
                this.renderer.destroy();
                this.renderer = null;
                this.createRenderer()
                this.initializeCanvas()
            }
        },
        valueScaleBorder: function(val) {
            if (val === undefined){
                // if no border defined and watcher fired -> emit slider change event
                this.$emit("slider-change", [
                    this.minValueRobust,
                    this.maxValueRobust,
                    this.minValue,
                    this.maxValue
                ]);
            }
        },
        colormap: function() {
            // if colormap changes -> reset min and max
            this.createColorMap(this.minValueRobust, this.maxValueRobust);
            this.drawHeatmap();
        },
        height: function() {
            this.resizeCanvas(this.visualizationSize, this.visualizationSize);
            this.drawHeatmap();
        },
        width: function() {
            this.resizeCanvas(this.visualizationSize, this.visualizationSize);
            this.drawHeatmap();
        },
        minHeatmapValue: function() {
            if (this.minHeatmapValue && this.maxHeatmapValue) {
                this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
            } else {
                this.createColorMap(this.minValueRobust, this.maxValueRobust);
            }
            this.drawHeatmap();
        },
        maxHeatmapValue: function() {
            if (this.minHeatmapValue && this.maxHeatmapValue) {
                this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
            } else {
                this.createColorMap(this.minValueRobust, this.maxValueRobust);
            }
            this.drawHeatmap();
        }
    },
    mounted: function() {
        // initialize min from prop if defined
        if (this.minHeatmapValue && this.maxHeatmapValue) {
            this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
        } else {
            this.createColorMap(this.minValueRobust, this.maxValueRobust);
        }
        this.createRenderer();
        this.initializeCanvas();
        this.drawHeatmap();
        // emit slider change to set initial values in pileupWidget
        this.$emit("slider-change", [
            this.minValueRobust,
            this.maxValueRobust,
            this.minValue,
            this.maxValue
        ]);
    },
    beforeDestroy: function() {
        /*
            destroy everything and release all webgl contexts
            All things that reference any webgl components need to be nulled
            Then, we need to hope that the webgl context is garbage collected
            before we reach >16 contexts.
        */
        //
        this.destroyPseudoCanvas();
        this.stage.destroy();
        this.stage = null;
        // remove renderer view
        if (this.$refs["canvasDiv"]){
            this.$refs["canvasDiv"].removeChild(this.renderer.view);
        }
        this.renderer.destroy();
        this.renderer = null;
        this.texture = null;
        this.sprite = null;
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

.small-margin-left-right {
    margin-left: 5px;
    margin-right: 5px;
    margin-top: 0px;
    margin-bottom: 0px;
}

.small-margin-left-right-top {
    margin-left: 5px;
    margin-right: 5px;
    margin-top: 5px;
    margin-bottom: 0px
}
</style>
