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
import enrichmentDistribution from "./enrichmentDistribution.vue"
import enrichmentRanks from "./enrichmentRanks.vue"
import {max_array_along_rows, select_column} from "../../functions" 

export default {
    name: "associationPlot",
    components: {
        enrichmentDistribution,
        enrichmentRanks
    },
    props: {
        plotData: Object,
        width: Number,
        height: Number,
        collectionNames: Array,
        intervalSize: Number,
        selectedColumn: Number
    },
    computed: {
        rankPlotHeight: function(){
            return this.height * 0.7
        },
        distributionPlotHeight: function(){
            return this.height * 0.3
        },
        enrichmentData: function(){
            return max_array_along_rows(this.plotData["data"], this.plotData["shape"])
        },
        currentColumn: function(){
            if (this.selectedColumn == undefined){
                return Math.floor(this.plotData["shape"][1]/2)
            }else{
                return this.selectedColumn
            }
        },
        rankData: function(){
            return select_column(this.plotData["data"], this.plotData["shape"], this.currentColumn)
        }
    },
    methods: {
        transmitEvent: function(index){
            this.$emit("barclick", index)
        }
    }
}

</script>

<style scoped>

.no-padding {
    padding: 0px
}

</style>