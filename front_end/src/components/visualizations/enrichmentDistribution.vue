<template>
    <div :id="divName" class="no-margin" />
</template>

<script>
import * as d3 from "d3";
import { formattingMixin } from "../../mixins";

export default {
    name: "enrichmentDistribution",
    mixins: [formattingMixin],
    props: {
        rawData: Array,
        width: Number,
        height: Number,
        intervalSize: Number,
        currentColumn: Number,
        binsize: Number
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
            return `enrichmentDistribution${this.id}`;
        },
        plotData: function(){
            // encode index in data
            return this.rawData.map((elem, i) => {
                return {
                    "value": elem,
                    "index": i
                }
            })
        },
        margin: function () {
            return {
                top: this.height * 0.09,
                bottom: this.height * 0.4,
                right: this.width * 0.1,
                left: this.width * 0.1,
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
            this.xScale = d3
                .scaleBand()
                .domain(d3.range(0, this.plotData.length))
                .range([0, this.plotWidth])
                .paddingInner(0.2)
                .paddingOuter(0.05);
            this.yScale = d3
                .scaleLinear()
                .domain([0, this.maxVal])
                .range([0, this.plotHeight]);
        },
        xAxisGenerator: function (args) {
            // x-axis generator function
            return d3
                .axisBottom(this.xScale)
                .tickFormat(this.xAxisFormatter)
                .tickSize(0)(args);
        },
        yAxisGenerator: function (args) {
            // y-axis generator function
            return d3
                .axisLeft(this.yScale)
                .tickFormat(this.yAxisFormatter)
                .tickSize(0)
                .ticks(3)(args);
        },
        yAxisFormatter: function (val, index) {
            if (index % 2 == 0) {
                return Math.floor((this.maxVal - val) * 10) / 10;
            }
        },
        xAxisFormatter: function (val, index) {
            if (
                index % Math.floor(this.plotData.length / 5) == 0
            ) {
                if (!isNaN(this.intervalSize)) {
                    return (
                        Math.floor(
                            (-this.intervalSize +
                                index *
                                    Math.floor(
                                        (this.intervalSize * 2) /
                                            this.plotData.length
                                    )) /
                                1000
                        ) + " kb"
                    );
                }
                // this is variable region, x-axis format in percent
                return  (-20 + index * this.binsize) + " %"
            }
            return "";
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
                .attr("x", (d) => {
                    return this.xScale(d.index);
                })
                .attr("width", this.xScale.bandwidth())
                .attr("fill", (d) => {
                    if (d.index == this.currentColumn) {
                        return "red";
                    }
                    return "grey";
                })
                .attr("y", () => {
                    return this.plotHeight;
                })
                .attr("height", 0)
                .transition()
                .delay((d) => {
                    return (this.xScale(d.index) / 150 / this.plotData.length) * 1000;
                })
                .duration(500)
                .attr("y", (d) => {
                    return this.plotHeight - this.yScale(d.value);
                })
                .attr("height", (d) => {
                    return this.yScale(d.value);
                });
            // add event listener
            this.svg
                .selectAll("rect")
                .on("click", this.handleBarClick)
        },
        handleBarClick: function(e, d){
            this.$emit("barclick", d.index)
        },
        updateBarChart: function () {
            /*
        Updates bar chart with new data
      */
            // put in new data and store selection
            let rect = this.svg.selectAll("rect").data(this.plotData);
            // remove old data
            rect.exit()
                .transition()
                .duration(500)
                .attr("y", () => {
                    return this.plotHeight;
                })
                .attr("height", 0)
                .remove();
            // add new ones
            rect.enter()
                .append("rect")
                .attr("x", (d) => {
                    return this.xScale(d.index);
                })
                .attr("width", this.xScale.bandwidth())
                .attr("fill", (d) => {
                    if (d.index == this.currentColumn) {
                        return "red";
                    }
                    return "grey";
                })
                .attr("y", () => {
                    return this.plotHeight;
                })
                .attr("height", 0)
                .transition()
                .delay((d) => {
                    return (this.xScale(d.index) / 150 / this.plotData.length) * 1000;
                })
                .duration(500)
                .attr("y", (d) => {
                    return this.plotHeight - this.yScale(d.value);
                })
                .attr("height", (d) => {
                    return this.yScale(d.value);
                });
            // reposition old bars
            rect.transition()
                .duration(500)
                .attr("x", (d) => {
                    return this.xScale(d.index);
                })
                .attr("fill", (d) => {
                    if (d.index == this.currentColumn) {
                        return "red";
                    }
                    return "grey";
                })
                .attr("width", this.xScale.bandwidth())
                .attr("y", (d) => {
                    return this.plotHeight - this.yScale(d.value);
                })
                .attr("height", (d) => {
                    return this.yScale(d.value);
                });
            // add event listener
            this.svg
                .selectAll("rect")
                .on("click", this.handleBarClick)
        },
        updateAxes: function () {
            /*
        updates axes with new data
      */
            //Update x-axis
            this.svg
                .select(".x.axis")
                .transition()
                .duration(500)
                .call(this.xAxisGenerator)
                .selectAll("text")
                .attr("y", 10)
                .attr("x", 0);
            //Update y-axis
            this.svg
                .select(".y.axis")
                .transition()
                .duration(500)
                .call(this.yAxisGenerator);
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
            this.createScales();
            this.updateAxes();
            this.updateBarChart();
        },
        currentColumn: function(){
            this.createScales();
            this.updateAxes();
            this.updateBarChart();
        }
    },
};
</script>

<style>
.no-margin {
    margin: 0px;
}
</style>