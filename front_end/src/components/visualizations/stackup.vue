<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <!-- Pileup display -->
                <md-content class="center-horizontal md-elevation-1">
                    <div class="small-margin" ref="canvasDiv"/>
                    <!-- this prevents drag events -->
                    <div draggable="true" @dragstart.prevent.stop class="slider-container">
                        <double-range-slider
                        :sliderWidth="width/2"
                        :sliderMin="minValue"
                        :sliderMax="maxValue"
                        :sliderPositionMin="minHeatmapValue"
                        :sliderPositionMax="maxHeatmapValue"
                        @slider-change="handleColorChange"
                        />
                    </div>
                </md-content>
            </md-list-item>
        </md-list>
    </div>
</template>
<script>
import * as PIXI from 'pixi.js'
import { getScale } from "../../colorScales.js";
import doubleRangeSlider from '../ui/doubleRangeSlider.vue';

export default {
    name: "stackup",
    components: {
        doubleRangeSlider
    },
    props: {
        title: String,
        stackupData: Object,
        width: Number,
        height: Number,
        stackupID: Number,
        minHeatmapValue: Number,
        maxHeatmapValue: Number
    },
    computed: {
        stackupValues: function(){
            return this.stackupData["data"]
        },
        stackupDimensions: function(){
            return this.stackupData["shape"]
        },
        stackupDtype: function(){
            return this.stackupData["dtype"]
        },
        minValue: function() {
            // find minimum by hand because Math.min cannot handle more than
            // a few k elements...
            var min = Infinity
            for (var val of this.stackupValues){
                if (val){
                    if (val < min){
                        min = val
                    }
                }
            }
            return min
        },
        maxValue: function() {
            // maximum value for heatmap lookuptable = maximum value in data
            // filter out nans and extract values into array
            var max = 0
            for (var val of this.stackupValues){
                if (val){
                    if (val > max){
                        max = val
                    }
                }
            }
            return max
        },
        rgbArray: function() {
            // array with rgba values for pixi Texture.fromBuffer
            var bufferArray = [];
            for (var element of this.stackupValues){
                // convert rgb values into range between 0 and 1
                var colorValues = this.colorScale(element).split(/[\,,(,)]/).slice(1,4).map((element) => Number(element)/255);
                // add to bufferarray
                for (var value of colorValues){
                    bufferArray.push(value)
                }
                // add saturation of rgba to 1
                bufferArray.push(1.0)
            }
            return new Float32Array(bufferArray)
        }
    },
    data: function() {
        return {
            renderer: new PIXI.autoDetectRenderer({
                width: this.width,
                height: this.height
            }),
            stage: undefined,
            texture: undefined,
            sprite: undefined,
            colorScale: undefined
        };
    },
    methods: {
        handleColorChange: function(data){
            this.$emit('slider-change', data) // propagate up to store in store
            this.createColorMap(...data)
            this.drawHeatmap()
        },
        createColorMap: function(minVal, maxVal) {
            this.colorScale = getScale(minVal, maxVal, "stackup")
        },
        drawHeatmap: function() {
            this.texture = PIXI.Texture.fromBuffer(this.rgbArray, this.stackupDimensions[1], this.stackupDimensions[0]);
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
            this.stage = new PIXI.Container();
        }
    },
    mounted: function() {
        // initialize min from prop if defined
        if (this.minHeatmapValue && this.maxHeatmapValue){
            this.createColorMap(this.minHeatmapValue, this.maxHeatmapValue)
        }else{
            this.createColorMap(this.minValue, this.maxValue)
        }
        this.initializeCanvas();
        this.drawHeatmap()
    },
    beforeDestroy: function() {
        // destroy canvas
        if (this.stage){
            this.stage.destroy();
        }
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

.slider-container {
    width:100%;
    height:20px;
    margin:0 auto;
}

</style>
