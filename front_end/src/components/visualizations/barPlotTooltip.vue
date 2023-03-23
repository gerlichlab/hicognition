<template>
    <md-card
        :style="tooltipStyle"
        v-show="showTooltip && clusterIDs.length !== 0"
    >
        <div class="md-layout-item md-size-100 blue-background">
            <span class="md-caption padding-left">{{ dataInfo }}</span>
        </div>
        <md-card-content class="no-padding">
            <embedding-distribution
                v-if="clusterIDs.length !== 0"
                :rawData="selectedDistribution"
                :width="width"
                :height="plotSize"
                :datasetNames="datasetNames"
                :minValue="minValue"
                :maxValue="maxValue"
            />
        </md-card-content>
        <md-card-actions v-if="showControls">
            <md-button @click="$emit('close-controls')">Close</md-button>
            <md-button @click="showDialog = true"
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
            >The region was added successfully!</md-snackbar
        >
    </md-card>
</template>

<script>
import { apiMixin } from "../../mixins";
import { select_rows, mean_along_rows } from "../../functions";
import embeddingDistribution from "../visualizations/embeddingDistribution.vue";

export default {
    name: "BarplotTooltip",
    components: { embeddingDistribution },
    mixins: [apiMixin],
    props: {
        id: Number,
        width: Number,
        height: Number,
        showTooltip: Boolean,
        averageValues: Object,
        showControls: Boolean,
        tooltipOffsetLeft: Number,
        tooltipOffsetTop: Number,
        clusterIDs: Array,
        embeddingID: Number,
        collectionName: String,
        regionName: String,
        datasetNames: Array,
        clusterCounts: Map
    },
    data: function() {
        return {
            tooltipStyle: {
                position: "absolute",
                "background-color": "white",
                top: "0px",
                left: "0px",
                "z-index": "10",
                width: `${this.width}px`,
                height: `${this.height}px`
            },
            showDialog: false,
            newRegionName: `${this.regionName} | ${this.datasetName}: cluster ${this.clusterIDs}`,
            datasetSaved: false
        };
    },
    computed: {
        totalRegions: function() {
            let sum = 0;
            for (let [key, value] of this.clusterCounts) {
                sum += value;
            }
            return sum;
        },
        selectedCounts: function(){
            let sum = 0;
            for (let [key, value] of this.clusterCounts) {
                if (this.clusterIDs.includes(key)){
                    sum += value;
                }
            }
            return sum;
        },
        dataInfo: function() {
            if (
                this.clusterCounts !== undefined &&
               this.selectedCounts !== undefined
            ) {
                return `Cluster: ${this.clusterIDs} | ${this.selectedCounts} 
                            /${this.totalRegions} Regions`;
            }
            return `Cluster: ${this.clusterIDs}`;
        },
        plotSize: function() {
            return this.width * 0.8;
        },
        selectedDistribution: function() {
            if (this.clusterIDs.length != 0) {
                let selected_rows = select_rows(
                    this.averageValues.data,
                    this.averageValues.shape,
                    this.clusterIDs
                );
                // reduce selection along rows
                return mean_along_rows(selected_rows.result, selected_rows.shape)
            }
        },
        minValue: function() {
            // computes minimum value of data passed
            let minVal = Infinity;
            for (let elem of this.averageValues.data) {
                if (elem < minVal) {
                    minVal = elem;
                }
            }
            return minVal;
        },
        maxValue: function() {
            // computes maximum value of data passed
            let maxVal = -Infinity;
            for (let elem of this.averageValues.data) {
                if (elem > maxVal) {
                    maxVal = elem;
                }
            }
            return maxVal;
        }
    },
    methods: {
        handleSubmission: function() {
            // check whether there is a name
            if (this.newRegionName.length === 0) {
                console.log("no region name provided");
                return;
            }
            // create form
            let formData = new FormData();
            formData.append("name", this.newRegionName);
            formData.append("cluster_ids", JSON.stringify(this.clusterIDs))
            // do api call
            this.postData(
                `embeddingIntervalData/${this.embeddingID}/createRegion/`,
                formData
            ).then(response => {
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                    // fetch datasets so that they are available in table
                    this.fetchAndStoreDatasets();
                }
            });
        }
    },
    watch: {
        tooltipOffsetLeft: function(val) {
            this.tooltipStyle["left"] = `${val}px`;
        },
        tooltipOffsetTop: function(val) {
            this.tooltipStyle["top"] = `${val}px`;
        },
        height: function(val) {
            this.tooltipStyle["height"] = `${val}px`;
        },
        width: function(val) {
            this.tooltipStyle["width"] = `${val}px`;
        },
        showControls: function(val) {
            this.newRegionName = `${this.regionName}-${this.datasetName}: cluster ${this.clusterIDs}`;
            if (!val) {
                this.tooltipStyle["height"] = `${this.height}px`;
            }
        }
    }
};
</script>

<style>
.no-margin {
    margin: 0px;
}

.no-padding {
    padding: 0px !important;
}

.blue-background {
    background: var(--md-theme-default-primary);
}

.padding-left {
    padding-left: 10px;
}
</style>
