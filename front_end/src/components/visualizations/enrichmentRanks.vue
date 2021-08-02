<template>
    <div :id="plotID"/>
</template>

<script>
export default {
    name: "enrichmentRanks",
    props: {
        plotData: Array,
        width: Number,
        height: Number
    },
    data: function(){
        return {
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            id: Math.round(Math.random() * 1000000)
        }
    },
    computed: {
        plotID: function(){
            return `enrichmentRanks${this.id}`
        }
    }
}
</script>