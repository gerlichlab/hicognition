<template>
    <md-card :style="tooltipStyle" v-show="showTooltip && thumbnail">
        <md-card-content>
            <heatmap
                v-if="thumbnail"
                :stackupID="id"
                :width="heatmapSize"
                :height="heatmapSize"
                :stackupData="thumbnail"
                :colormap="colormap"
                :minHeatmapValue="minHeatmap"
                :maxHeatmapValue="maxHeatmap"
                :minHeatmapRange="minHeatmapRange"
                :maxHeatmapRange="maxHeatmapRange"
                :allowValueScaleChange="showControls"
                @slider-change="handleSliderChange"
                :log="true"
            />
        </md-card-content>
        <md-card-actions v-if="showControls">
            <md-button @click="$emit('close-controls')" class="md-raised md-accent">Close</md-button>
            <md-button class="md-raised md-primary" @click="showDialog = true">Create Region</md-button>
        </md-card-actions>
    <md-dialog-prompt
      :md-active.sync="showDialog"
      v-model="newRegionName"
      md-title="Enter a region name"
      md-input-maxlength="30"
      md-confirm-text="Submit"
      @md-confirm="handleSubmission"
    />
    <md-snackbar :md-active.sync="datasetSaved"
        >The region was added succesfully!</md-snackbar
    >
    </md-card>
</template>

<script>
import heatmap from "../visualizations/heatmap.vue";
import { apiMixin } from "../../mixins";

export default {
    name: "HeatmapTooltip",
    components: { heatmap },
    mixins: [apiMixin],
    props: {
        id: Number,
        width: Number,
        height: Number,
        colormap: String,
        allowValueScaleChange: Boolean,
        showTooltip: Boolean,
        thumbnail: Object,
        showControls: Boolean,
        tooltipOffsetLeft: Number,
        tooltipOffsetTop: Number,
        clusterID: Number,
        embeddingID: Number,
        datasetName: String,
        regionName: String
    },
    data: function() {
        return {
        tooltipStyle: {
                    position: "absolute",
                    "background-color": "white",
                    top: "0px",
                    left: "0px",
                    "z-index": "100",
                    "width": `${this.width}px`,
                    "height": `${this.height}px`
                },
        showDialog: false,
        newRegionName: `${this.regionName} | ${this.datasetName}: cluster ${this.clusterID}`,
        datasetSaved: false,
        minHeatmap: undefined,
        maxHeatmap: undefined,
        minHeatmapRange: undefined,
        maxHeatmapRange: undefined
        }
    },
    computed: {
        heatmapSize: function() {
            return this.width * 0.8;
        }
    },
    methods: {
        handleSliderChange: function(data) {
            this.setColorScale(data);
        },
        setColorScale: function (data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            this.minHeatmap = data[0];
            this.maxHeatmap = data[1];
            this.minHeatmapRange = data[2]
            this.maxHeatmapRange = data[3]
        },
        resetColorScale: function () {
            /*
                resets colorscale to undefined
            */
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
            this.minHeatmapRange = undefined;
            this.maxHeatmapRange = undefined;
        },
        handleSubmission: function(){
            // check whether there is a name
            if (this.newRegionName.length === 0) {
                console.log("no region name provided")
                return
            }
            // create form
            let formData = new FormData();
            formData.append("name", this.newRegionName)
            // do api call
            this.postData(`embeddingIntervalData/${this.embeddingID}/${this.clusterID}/create/`, formData).then(response => {
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                }
            });

        }
    },
    watch: {
        tooltipOffsetLeft: function(val){
            this.tooltipStyle["left"] = `${val}px`
        },
        tooltipOffsetTop: function(val){
            this.tooltipStyle["top"] = `${val}px`
        },
        height: function(val){
            this.tooltipStyle["height"] = `${val}px`
        },
        width: function(val){
            this.tooltipStyle["width"] = `${val}px`
        },
        showControls: function(){
            this.newRegionName = `${this.regionName}-${this.datasetName}: cluster ${this.clusterID}`
        },
        thumbnail: function(){
            this.resetColorScale()
        }
    }
};
</script>

<style>
.no-margin {
    margin: 0px;
}

.no-padding {
    padding: 0px;
}
</style>
