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
import { rectBin, select_column } from "../../functions";

export default {
    name: "embeddingPlot",
    mixins: [formattingMixin],
    props: {
        rawData: Object,
        width: Number,
        height: Number,
        overlay: String,
    },
    data: function () {
        return {
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            valueScale: undefined,
            id: Math.round(Math.random() * 1000000),
            size: 50,
        };
    },
    computed: {
        divName: function () {
            return `embedding${this.id}`;
        },
        overlayValues: function () {
            if (this.overlay == "density") {
                return undefined;
            }
            return select_column(
                this.rawData["features"]["data"],
                this.rawData["features"]["shape"],
                Number(this.overlay)
            );
        },
        maxDensity: function () {
            let max = -Infinity;
            for (let el of this.rectBin) {
                if (el.value > max) {
                    max = el.value;
                }
            }
            return max;
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
        rectBin: function () {
            return rectBin(this.size, this.plotData, this.plotBoundaries);
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
                top: this.height * 0,
                bottom: this.height * 0,
                right: this.width * 0,
                left: this.width * 0,
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
                .scaleBand()
                .domain(d3.range(0, this.size))
                .range([0, this.plotWidth]);
            this.yScale = d3
                .scaleBand()
                .domain(d3.range(0, this.size))
                .range([0, this.plotHeight]);
            this.valueScale = d3
                .scaleSequential(d3.interpolateReds)
                .domain([0, this.maxDensity]);
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
            this.drawRects();
        },
        updateRects: function () {
            this.svg
                .selectAll("rect")
                .data(this.rectBin)
                .transition()
                .attr("x", (d) => Math.floor(Math.random() * this.plotWidth))
                .attr("y", (d) => Math.floor(Math.random() * this.plotHeight))
                .attr("fill", (d, i) => {
                    if (this.overlay == "density") {
                        return this.valueScale(d.value);
                    }
                })
                .transition()
                .delay(
                    (d) =>
                        Math.sqrt(
                            this.xScale(d.x) * this.xScale(d.x) +
                                this.yScale(d.y) * this.yScale(d.y)
                        ) * 2
                )
                .attr("x", (d) => this.xScale(d.x))
                .attr("y", (d) => this.yScale(d.y));
        },
        drawRects: function () {
            this.svg
                .selectAll("rect")
                .data(this.rectBin)
                .enter()
                .append("rect")
                .attr("fill", (d, i) => {
                    if (this.overlay == "density") {
                        return this.valueScale(d.value);
                    }
                })
                .attr("x", (d) => this.xScale(d.x))
                .attr("y", (d) => this.yScale(d.y))
                .attr("width", this.xScale.bandwidth())
                .attr("height", this.yScale.bandwidth());
        },
    },
    mounted: function () {
        this.createScales();
        this.createChart();
    },
    watch: {
        rawData: function () {
            this.createScales();
            this.updateRects();
        },
    },
};
</script>
