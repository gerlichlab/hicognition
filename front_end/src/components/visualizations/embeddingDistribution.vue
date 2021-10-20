<template>
    <div :id="divName" class="no-margin" />
</template>

<script>
import * as d3 from "d3";
import { formattingMixin } from "../../mixins";

export default {
    name: "embeddingDistribution",
    mixins: [formattingMixin],
    props: {
        rawData: Array,
        width: Number,
        height: Number,
        collectionNames: Array
    },
    data: function () {
        return {
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            id: Math.round(Math.random() * 1000000),
        };
    },
    computed: {
        divName: function () {
            return `embeddingDistribution${this.id}`;
        },
        plotData: function(){
            if (this.rawData) {
            // encode index in data
                return this.rawData.map((elem, i) => {
                    return {
                        "value": elem,
                        "index": i
                    }
                })
            }
        },
        margin: function () {
            return {
                top: this.height * 0.09,
                bottom: this.height * 0.3,
                right: this.width * 0.1,
                left: this.width * 0.2,
            };
        },
        maxVal: function () {
            // computes maximum value of data passed
            let maxVal = -Infinity;
            for (let elem of this.rawData) {
                if (elem > maxVal) {
                    maxVal = elem;
                }
            }
            return maxVal;
        },
        svgName: function () {
            return `svg${this.id}`;
        },
        plotWidth: function () {
            // width of the plotting area without margins
            return this.width - this.margin.left - this.margin.right;
        },
        plotHeight: function () {
            // height of the plotting area without margins
            return this.height - this.margin.top - this.margin.bottom;
        },
    },
    methods: {
        createScales: function () {
            /*
        Creates scaling functions for plot. Map data values into
        coordinates on the plot
      */
            this.yScale = d3
                .scaleBand()
                .domain(d3.range(0, this.plotData.length))
                .range([0, this.plotHeight])
                .paddingInner(0.2)
                .paddingOuter(0.05);
            this.xScale = d3
                .scaleLinear()
                .domain([0, this.maxVal])
                .range([0, this.plotWidth]);
        },
        xAxisGenerator: function (args) {
            // x-axis generator function
            return d3
                .axisBottom(this.xScale)
                .tickSize(0)
                .ticks(3)
                .tickFormat(this.xAxisFormatter)(args);
        },
        yAxisGenerator: function (args) {
            // y-axis generator function
            return d3
                .axisLeft(this.yScale)
                .tickFormat(this.yAxisFormatter)
                .tickSize(0)(args);
        },
        getEllipsisName: function(val) {
            if (val.length > 10) {
                return val.slice(0, 10) + "..."
            }
            return val
        },
        yAxisFormatter: function (val, index) {
            return this.getEllipsisName(this.collectionNames[index].name)
        },
        xAxisFormatter: function(val, index){
            return `${val} %`
        },
        createBars: function () {
            /*
        creates bars of barchart and adds them to this.svg
      */
            this.svg
                .selectAll("rect")
                .data(this.plotData)
                .enter()
                .append("rect")
                .attr("y", (d) => {
                    return this.yScale(d.index);
                })
                .attr("x", 0)
                .attr("height", this.yScale.bandwidth())
                .attr("fill", "red")
                .attr("width", 0)
                .transition()
                .delay((d) => {
                    return (this.yScale(d.index) / 150 / this.plotData.length) * 1000;
                })
                .duration(500)
                .attr("width", (d) => {
                    return this.xScale(d.value);
                });
        },
        createAxes: function () {
            /*       
               Adds axes to an svg object at this.svg
            */
            // add x axes
            this.svg
                .append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.plotHeight + ")")
                .call(this.xAxisGenerator)
                .selectAll("text")
                .attr("y", 10)
                .attr("x", 0);
            // add yaxes
            this.svg
                .append("g")
                .attr("class", "y axis")
                .call(this.yAxisGenerator);
        },
        createChart: function () {
            /*
        Wrapper function that creates svg and adds
        chosen visualization
      */
            // creating svg object
            this.svg = d3
                .select(`#${this.divName}`)
                .append("svg")
                .attr("id", this.svgName)
                .attr("width", this.width)
                .attr("height", this.height)
                .append("g")
                .attr(
                    "transform",
                    "translate(" +
                        this.margin.left +
                        "," +
                        this.margin.top +
                        ")"
                );
            // draw chart
            this.createScales();
            this.createAxes();
            this.createBars();
        },
    },
    mounted: function () {
        this.createScales();
        this.createChart();
    },
    watch: {
        height: function () {
            d3.select(`#${this.svgName}`).remove();
            this.createScales();
            this.createChart();
        },
        width: function () {
            d3.select(`#${this.svgName}`).remove();
            this.createScales();
            this.createChart();
        },
        plotData: function () {
            d3.select(`#${this.svgName}`).remove();
            this.createScales();
            this.createChart();
        },
    },
};
</script>

<style>
.no-margin {
    margin: 0px;
}
</style>