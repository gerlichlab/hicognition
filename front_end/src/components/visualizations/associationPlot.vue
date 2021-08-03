<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <enrichment-distribution
                :data="enrichmentData"
                :width="width"
                :height="distributionPlotHeight"
                :intervalSize="intervalSize"
                />
                <enrichment-ranks 
                :data="rankData"
                :width="width"
                :height="rankPlotHeight"
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
        intervalSize: Number
    },
    data: function(){
        return {
            selectedColumn: undefined
        }
    },
    computed: {
        rankPlotHeight: function(){
            return this.height * 0.8
        },
        distributionPlotHeight: function(){
            return this.height * 0.2
        },
        enrichmentData: function(){
            return max_array_along_rows(this.plotData["data"], this.plotData["shape"])
        },
        rankData: function(){
            if (this.selectedColumn == undefined){
                // take center
                let center_column = Math.floor(this.plotData["shape"][1]/2)
                return select_column(this.plotData["data"], this.plotData["shape"], center_column)
            }
            return select_column(this.plotData["data"], this.plotData["shape"], this.selectedColumn)
        }
    }
}

</script>