<template>
    <div :id="divName" class="small-margin" />
</template>

<script>
import * as d3 from "d3";

export default {
    name: "enrichmentRanks",
    props: {
        data: Array,
        width: Number,
        height: Number,
        collectionNames: Array,
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
            return `enrichmentRanks${this.id}`;
        },
        margin: function () {
            return {
                top: this.height * 0.09,
                bottom: this.height * 0.1,
                right: this.width * 0.1,
                left: this.width * 0.1,
            };
        },
        names: function () {
            return this.plotData.map((elem) => elem.name);
        },
        plotData: function () {
            /*
                Construct rank data
            */
            let namedData = this.data.map((elem, index) => {
                return {
                    value: elem,
                    name: this.collectionNames[index],
                };
            });
            // return sorted data. Array needs to be copied becuase computed values cannot mutate properties
            return [...namedData].sort((a, b) => a.value - b.value);
        },
        maxVal: function () {
            // computes maximum value of data passed
            let maxVal = -Infinity;
            for (let elem of this.data) {
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
                .domain(this.names)
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
                .tickSize(0)
                .ticks(3)
                .tickFormat(this.yAxisFormatter)(args);
        },
        yAxisFormatter: function (val) {
            return Math.floor((this.maxVal - val) * 10) / 10;
        },
        xAxisFormatter: function (val, index) {
            if (this.data.length < 5){
                return val
            }
            if (index % 2 == 0) {
                return `Rank ${index}`;
            }
        },
        createCircles: function () {
            /*
        creates bars of barchart and adds them to this.svg
      */
            this.svg
                .selectAll("circle")
                .data(this.plotData)
                .enter()
                .append("circle")
                .attr("r", (d) => {
                    if (d.value) {
                        return 5;
                    }
                    return 0;
                })
                .attr("cx", (d) => {
                    return this.xScale(d.name) + this.xScale.bandwidth() / 2;
                })
                .attr("fill", "red")
                .attr("cy", () => {
                    return this.plotHeight;
                })
                .attr("height", 0)
                .transition()
                .delay((d) => {
                    return (
                        (this.xScale(d.name) / 150 / this.data.length) * 1000
                    );
                })
                .duration(500)
                .attr("cy", (d) => {
                    if (d.value) {
                        return this.plotHeight - this.yScale(d.value);
                    }
                    return 0;
                })
                .attr("height", (d) => {
                    return this.yScale(d.value);
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
            this.createCircles();
        },
    },
    mounted: function () {
        this.createScales();
        this.createChart();
    },
};
</script>

<style>
.small-margin {
    margin: 0px;
}
</style>