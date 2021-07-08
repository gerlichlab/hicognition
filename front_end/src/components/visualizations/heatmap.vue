<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <!-- this prevents drag events to allow slider change without causing widget drag -->
                <div :style="colorBarContainerStyle" draggable="true" @dragstart.prevent.stop>
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
                <md-content class="center-horizontal md-elevation-0">
                    <div class="small-margin" ref="canvasDiv" />
                </md-content>
            </md-list-item>
        </md-list>
    </div>
</template>
<script>
import * as PIXI from "pixi.js-legacy";
import { getScale } from "../../colorScales.js";
import colorBarSlider from "../ui/colorBarSlider.vue"
import { getPercentile, getPerMilRank } from "../../functions";

const NAN_COLOR = [255, 255, 255]; // white nan color

// set pixi scale mode

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST

export default {
    name: "heatmap",
    components: {
        colorBarSlider
    },
    props: {
        title: String,
        stackupData: Object,
        width: Number,
        height: Number,
        sliderHeight: Number,
        stackupID: Number,
        minHeatmapValue: Number,
        maxHeatmapValue: Number,
        colormap: String,
        valueScaleColor: String,
        valueScaleBorder: String,
        allowValueScaleChange: Boolean,
        log: Boolean
    },
    computed: {
        colorBarContainerStyle: function() {
            return {
                "width": "17%",
                "height": this.height + "px",
                "display": "inline"
            }
        },
        sliderContainerStyle: function() {
            return {
                "width": "100%",
                "margin": "0 auto",
                "height": this.sliderHeight + "px",
                "display": "flex",
                "justify-content": "center",
                "align-content": "center"
            }
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
        minValueRobust: function(){
            if (this.minHeatmapValue){
                return this.minHeatmapValue
            }
            return getPercentile(this.stackupValues, 1)
        },
        maxValueRobust: function(){
            if (this.maxHeatmapValue){
                return this.maxHeatmapValue
            }
            return getPercentile(this.stackupValues, 99)
        },
        minValue: function() {
            // find minimum by hand because Math.min cannot handle more than
            // a few k elements...
            return getPerMilRank(this.stackupValues, 1)
        },
        maxValue: function() {
            // maximum value for heatmap lookuptable = maximum value in data
            // filter out nans and extract values into array
            return getPerMilRank(this.stackupValues, 999)
        },
        rgbArray: function() {
            // array with rgba values for pixi Texture.fromBuffer
            var bufferArray = [];
            for (var element of this.stackupValues) {
                // convert data into rgb values
                var colorValues;
                if (element) {
                    colorValues = this.colorScale(element)
                        .split(/[\,,(,)]/)
                        .slice(1, 4)
                        .map(element => Number(element));
                } else {
                    colorValues = NAN_COLOR;
                }
                // add to bufferarray
                for (var value of colorValues) {
                    bufferArray.push(value);
                }
                // add full saturation
                bufferArray.push(255);
            }
            return new Uint8ClampedArray(bufferArray);
        }
    },
    data: function() {
        return {
            renderer: new PIXI.CanvasRenderer({
                width: this.width,
                height: this.height
            }),
            stage: undefined,
            texture: undefined,
            sprite: undefined,
            colorScale: undefined,
            imageData: undefined,
            id : Math.round(Math.random() * 1000000),
            pseudoCanvasContext: undefined,
            pseudoCanvas: undefined

        };
    },
    methods: {
        destroyPseudoCanvas: function(){
            if (this.pseudoCanvas){
                this.pseudoCanvas.remove()
            }
        },
        createPseudoCanvas: function(){
            let canvas = document.createElement('canvas');
            canvas.id =`pseudoCanvas${this.id}`
            canvas.width = this.stackupDimensions[1];
            canvas.height = this.stackupDimensions[0];
            canvas.style.top = "50px"
            canvas.style.left= `-${this.width + 50}px`
            canvas.style.position = "absolute";
            document.body.appendChild(canvas);
            // store cnavas
            this.pseudoCanvas = canvas;
            // get canvas2d context
            this.pseudoCanvasContext = canvas.getContext('2d');
        },
        handleColorChange: function(data) {
            this.$emit("slider-change", data); // propagate up to store in store
            this.createColorMap(...data);
            this.drawHeatmap();
        },
        createColorMap: function(minVal, maxVal) {
            this.colorScale = getScale(minVal, maxVal, this.colormap);
        },
        resizeCanvas: function(width, height) {
            this.renderer.resize(width, height)
        },
        drawHeatmap: function() {
            // destroy old pseudocanvas if existing
            this.destroyPseudoCanvas()
            this.createPseudoCanvas()
            this.imageData = new ImageData(this.rgbArray, this.stackupDimensions[1], this.stackupDimensions[0])
            // add image to pseudocanvas
            this.pseudoCanvasContext.putImageData(this.imageData, 0, 0)
            // create texture form pseudocanvas
            this.texture = PIXI.Texture.from(this.pseudoCanvas)
            this.sprite = PIXI.Sprite.from(this.texture);
            // position sprite at top left and make it stretch the canvas
            this.sprite.x = 0;
            this.sprite.y = 0;
            this.sprite.width = this.width;
            this.sprite.height = this.height;
            // add and render
            this.stage.addChild(this.sprite);
            this.renderer.render(this.stage);
        },
        initializeCanvas: function() {
            // add the renderer view object into the canvas div
            this.$refs["canvasDiv"].appendChild(this.renderer.view);
            // create stage
            this.stage = new PIXI.Container()
        }
    },
    watch: {
        stackupData: function() {
            // rerender if stackupdata changes -> important for sorting
            if (this.minHeatmapValue && this.maxHeatmapValue) {
                this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
            } else {
                this.createColorMap(this.minValueRobust, this.maxValueRobust);
            }
            this.drawHeatmap();
        },
        colormap: function() {
            // if colormap changes -> reset min and max
            this.createColorMap(this.minValueRobust, this.maxValueRobust);
            this.drawHeatmap();
        },
        height: function(){
            this.resizeCanvas(this.width, this.height)
            this.drawHeatmap();
        },
        height: function(){
            this.resizeCanvas(this.width, this.height)
            this.drawHeatmap();
        },
        minHeatmapValue: function(){
            if (this.minHeatmapValue && this.maxHeatmapValue) {
                this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue);
            } else {
                this.createColorMap(this.minValueRobust, this.maxValueRobust);
            }
            this.drawHeatmap();
        },
        maxHeatmapValue: function(){
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
        this.initializeCanvas();
        this.drawHeatmap();
        // emit slider change to set initial values in pileupWidget
        this.$emit("slider-change", [this.minValueRobust, this.maxValueRobust]);
    },
    beforeDestroy: function() {
        /*
            destroy everything and release all webgl contexts
            All things that reference any webgl components need to be nulled
            Then, we need to hope that the webgl context is garbage collected
            before we reach >16 contexts.
        */
        //
        this.destroyPseudoCanvas()
        this.stage.destroy();
        this.stage = null;
        // remove renderer view
        this.$refs["canvasDiv"].removeChild(this.renderer.view);
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

</style>
