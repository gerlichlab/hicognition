<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <enrichment-distribution
                :width="width"
                :height="distributionPlotHeight"
                />
                <enrichment-ranks 
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
        height: Number
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
        }
    }
}

</script>