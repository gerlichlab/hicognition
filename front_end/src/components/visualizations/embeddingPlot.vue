<template>
    <md-list class="md-double-line">
        <md-list-item class="md-alignment-top-center">
            <div :id="divName" />
        </md-list-item>
    </md-list>
</template>

<script>
import * as d3 from "d3";
import { formattingMixin } from "../../mixins";

export default {
    name: "embeddingPlot",
    mixins: [formattingMixin],
    props: {
        rawData: Object,
        width: Number,
        height: Number,
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
            return `embedding${this.id}`;
        },
        plotData: function () {
            let embedding = this.rawData["embedding"]["data"];
            // get x and y coordinates
            let x_vals = [];
            let y_vals = [];
            for (let i = 0; i < embedding.length; i++) {
                if (i % 2 == 0) {
                    x_vals.push(embedding[i]);
                } else {
                    y_vals.push(embedding[i]);
                }
            }
            // construct plot objects
            let points = [];
            for (let j = 0; j < x_vals.length; j++) {
                points.push({
                    x: x_vals[j],
                    y: y_vals[j],
                });
            }
            return points;
        },
        plotBoundaries: function () {
            let minX = Infinity;
            let maxX = -Infinity;
            let minY = Infinity;
            let maxY = -Infinity;
            for (let el of this.plotData) {
                if (el.x < minX) {
                    minX = el.x;
                }
                if (el.x > maxX) {
                    maxX = el.x;
                }
                if (el.y < minY) {
                    minY = el.y;
                }
                if (el.y > maxY) {
                    maxY = el.y;
                }
            }
            return {
                minX: minX,
                maxX: maxX,
                minY: minY,
                maxY: maxY,
            };
        },
        margin: function () {
            return {
                top: this.height * 0.09,
                bottom: this.height * 0.1,
                right: this.width * 0.1,
                left: this.width * 0.1,
            };
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
                .scaleLinear()
                .domain([this.plotBoundaries.minX, this.plotBoundaries.maxX])
                .range([0, this.plotWidth]);
            this.yScale = d3
                .scaleLinear()
                .domain([this.plotBoundaries.minY, this.plotBoundaries.maxY])
                .range([0, this.plotHeight]);
        },
        xAxisFormatter: function (val) {
            return Math.floor(val * 10) / 10;
        },
        yAxisFormatter: function (val) {
            return Math.floor((this.plotBoundaries.maxY - val) * 10) / 10;
        },
        xAxisGenerator: function (args) {
            // x-axis generator function
            return d3
                .axisBottom(this.xScale)
                .tickFormat(this.xAxisFormatter)
                .tickSize(0)
                .ticks(4)(args);
        },
        yAxisGenerator: function (args) {
            // y-axis generator function
            return d3
                .axisLeft(this.yScale)
                .tickFormat(this.yAxisFormatter)
                .tickSize(0)
                .ticks(4)(args);
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
        updateChart: function () {
            this.createScales();
            this.updatePoints();
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
            this.createAxes();
            this.drawPoints();
        },
        drawPoints: function () {
            this.svg
                .selectAll("circels")
                .data(this.plotData)
                .enter()
                .append("circle")
                .attr("r", 5)
                .attr("fill", "red")
                .attr("opacity", 0)
                .attr("cx", (d) => this.xScale(d.x))
                .attr("cy", (d) => this.yScale(d.y))
                .transition()
                .duration(500)
                .attr("opacity", 0.3);
        },
        updatePoints: function () {
            let circels = this.svg.selectAll("circle").data(this.plotData);
            // reposition old ones
            circels
                .transition()
                .duration(500)
                .attr("cx", (d) => this.xScale(d.x))
                .attr("cy", (d) => this.yScale(d.y));
        },
    },
    mounted: function () {
        this.createScales();
        this.createChart();
    },
    watch: {
        rawData: function () {
            this.updateChart();
        },
    },
};
</script>
