<template>
    <div>
        <md-list class="md-double-line no-padding">
            <md-list-item class="md-alignment-top-center">
                <enrichment-distribution
                    :rawData="enrichmentData"
                    :width="width"
                    :height="distributionPlotHeight"
                    :intervalSize="intervalSize"
                    :currentColumn="currentColumn"
                    :binsize="binsize"
                    @barclick="transmitEvent"
                />
            </md-list-item>
            <md-list-item class="md-alignment-top-center">
                <enrichment-ranks
                    :rawData="rankData"
                    :width="width"
                    :height="rankPlotHeight"
                    :collectionNames="collectionNames"
                />
            </md-list-item>
        </md-list>
    </div>
</template>

<script>
import enrichmentDistribution from "./enrichmentDistribution.vue";
import enrichmentRanks from "./enrichmentRanks.vue";
import { max_array_along_rows, select_column } from "../../functions";

const EXPANSION_FACTOR = 0.2;

export default {
    name: "associationPlot",
    components: {
        enrichmentDistribution,
        enrichmentRanks,
    },
    props: {
        plotData: Object,
        width: Number,
        height: Number,
        collectionNames: Array,
        intervalSize: Number,
        selectedColumn: Number,
        binsize: Number,
    },
    computed: {
        intervalStartBin: function () {
            if (this.plotData) {
                let intervalSize = Math.round(
                    this.plotData["shape"][1] / (1 + 2 * EXPANSION_FACTOR)
                );
                return Math.round(intervalSize * EXPANSION_FACTOR);
            }
            return undefined;
        },
        rankPlotHeight: function () {
            return this.height * 0.7;
        },
        distributionPlotHeight: function () {
            return this.height * 0.3;
        },
        enrichmentData: function () {
            return max_array_along_rows(
                this.plotData["data"],
                this.plotData["shape"]
            );
        },
        currentColumn: function () {
            if (this.selectedColumn === undefined) {
                if (!isNaN(this.intervalSize)) {
                    return Math.floor(this.plotData["shape"][1] / 2);
                }
                return this.intervalStartBin;
            } else {
                return this.selectedColumn;
            }
        },
        rankData: function () {
            return select_column(
                this.plotData["data"],
                this.plotData["shape"],
                this.currentColumn
            );
        },
    },
    methods: {
        transmitEvent: function (index) {
            this.$emit("barclick", index);
        },
    },
};
</script>

<style scoped>
.no-padding {
    padding: 0px;
}
</style>
