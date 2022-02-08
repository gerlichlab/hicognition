<template>
    <md-card :style="tooltipStyle" v-show="showTooltip && clusterID !== undefined">
        <md-card-content class="no-padding">
            <embedding-distribution
                v-if="clusterID !== undefined"
                :rawData="selectedDistribution"
                :width="width"
                :height="plotSize"
                :datasetNames="datasetNames"
                :minValue="minValue"
                :maxValue="maxValue"

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
import { apiMixin } from "../../mixins";
import { select_row } from "../../functions";
import embeddingDistribution from "../visualizations/embeddingDistribution.vue"

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
        clusterID: Number,
        embeddingID: Number,
        collectionName: String,
        regionName: String,
        datasetNames: Array
    },
    data: function () {
        return {
            tooltipStyle: {
                position: "absolute",
                "background-color": "white",
                top: "0px",
                left: "0px",
                "z-index": "100",
                width: `${this.width}px`,
                height: `${this.height}px`,
            },
            showDialog: false,
            newRegionName: `${this.regionName} | ${this.datasetName}: cluster ${this.clusterID}`,
            datasetSaved: false
        };
    },
    computed: {
        plotSize: function () {
            return this.width * 0.8;
        },
        selectedDistribution: function () {
            if (this.clusterID !== undefined) {
                return select_row(
                    this.averageValues.data,
                    this.averageValues.shape,
                    this.clusterID
                );
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
        }
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
