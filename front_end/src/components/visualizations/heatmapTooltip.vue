<template>
    <md-card :style="tooltipStyle" v-show="showTooltip && thumbnail">
        <md-card-content class="no-padding">
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
                :log="isLog"
                :showInterval="isVariableSize"
            />
        </md-card-content>
            <md-card-actions v-if="showControls">
                <md-button
                    @click="$emit('close-controls')"
                    >Close</md-button
                >
                <md-button
                    @click="showDialog = true"
                    >Create Region</md-button
                >
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
import { select_row } from "../../functions";
import embeddingDistribution from "../visualizations/embeddingDistribution.vue"

export default {
    name: "HeatmapTooltip",
    components: { heatmap, embeddingDistribution },
    mixins: [apiMixin],
    props: {
        id: Number,
        width: Number,
        height: Number,
        colormap: String,
        allowValueScaleChange: Boolean,
        showTooltip: Boolean,
        thumbnail: Object,
        distributionData: Object,
        showControls: Boolean,
        tooltipOffsetLeft: Number,
        tooltipOffsetTop: Number,
        clusterID: Number,
        embeddingID: Number,
        datasetName: String,
        regionName: String,
        isLog: Boolean,
        minHeatmapAll: Number,
        maxHeatmapAll: Number,
        maxHeatmapAllRange: Number,
        minHeatmapAllRange: Number,
        isVariableSize: Boolean
    },
    data: function () {
        return {
            tooltipStyle: {
                position: "absolute",
                "background-color": "white",
                top: "0px",
                left: "0px",
                "z-index": "10",
                width: `${this.width}px`,
                height: `${this.height}px`,
            },
            showDialog: false,
            newRegionName: `${this.regionName} | ${this.datasetName}: cluster ${this.clusterID}`,
            datasetSaved: false,
            minHeatmapTarget: undefined,
            maxHeatmapTarget: undefined,
            minHeatmapRangeTarget: undefined,
            maxHeatmapRangeTarget: undefined
        };
    },
    computed: {
        distributionSize: function() {
            return 100
        },
        minHeatmap: function() {
            if (this.minHeatmapTarget) {
                return this.minHeatmapTarget
            }
            return this.minHeatmapAll
        },
        maxHeatmap: function() {
            if (this.maxHeatmapTarget) {
                return this.maxHeatmapTarget
            }
            return this.maxHeatmapAll
        },
        minHeatmapRange: function() {
            if (this.minHeatmapAllRange) {
                return this.minHeatmapAllRange
            }
            return this.minHeatmapRangeTarget
        },
        maxHeatmapRange: function() {
            if (this.maxHeatmapRangeTarget) {
                return this.maxHeatmapRangeTarget
            }
            return this.maxHeatmapAllRange
        },
        heatmapSize: function () {
            return this.width * 0.8;
        },
        selectedDistribution: function () {
            if (this.clusterID !== undefined) {
                return select_row(
                    this.distributionData.data,
                    this.distributionData.shape,
                    this.clusterID
                );
            }
        },
    },
    methods: {
        handleSliderChange: function (data) {
            this.setColorScale(data);
        },
        setColorScale: function (data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            this.minHeatmapTarget = data[0];
            this.maxHeatmapTarget = data[1];
            this.minHeatmapRangeTarget = data[2];
            this.maxHeatmapRangeTarget = data[3];
        },
        resetColorScale: function () {
            /*
                resets colorscale to undefined
            */
            this.minHeatmapTarget = undefined;
            this.maxHeatmapTarget = undefined;
            this.minHeatmapRangeTarget = undefined;
            this.maxHeatmapRangeTarget = undefined;
        },
        handleSubmission: function () {
            // check whether there is a name
            if (this.newRegionName.length === 0) {
                console.log("no region name provided");
                return;
            }
            // create form
            let formData = new FormData();
            formData.append("name", this.newRegionName);
            // do api call
            this.postData(
                `embeddingIntervalData/${this.embeddingID}/${this.clusterID}/create/`,
                formData
            ).then((response) => {
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                    // fetch datasets so that they are available in table
                    this.fetchAndStoreDatasets()
                }
            });
        },
    },
    watch: {
        tooltipOffsetLeft: function (val) {
            this.tooltipStyle["left"] = `${val}px`;
        },
        tooltipOffsetTop: function (val) {
            this.tooltipStyle["top"] = `${val}px`;
        },
        height: function (val) {
            this.tooltipStyle["height"] = `${val}px`;
        },
        width: function (val) {
            this.tooltipStyle["width"] = `${val}px`;
        },
        showControls: function (val) {
            this.newRegionName = `${this.regionName}-${this.datasetName}: cluster ${this.clusterID}`;
            if (!val) {
                this.tooltipStyle["height"] = `${this.height}px`;
            }
        },
        thumbnail: function () {
            this.resetColorScale();
        },
    },
};
</script>

<style>
.no-margin {
    margin: 0px;
}

.no-padding {
    padding: 0px !important;
}
</style>
