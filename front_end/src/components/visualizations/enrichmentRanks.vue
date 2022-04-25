<template>
    <div :id="divName" class="no-margin" />
</template>

<script>
import * as d3 from "d3";

const key = (d) => {
    return d.name;
};

export default {
    name: "enrichmentRanks",
    props: {
        rawData: Array,
        width: Number,
        height: Number,
        collectionNames: Array,
    },
    data: function () {
        return {
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            tooltip: undefined,
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
            let namedData = this.rawData.map((elem, index) => {
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
                .domain(this.names)
                .range([0, this.plotWidth])
                .paddingInner(0.2)
                .paddingOuter(0.05);
            this.yScale = d3
                .scaleLinear()
                .domain([0, this.maxVal])
                .range([0, this.plotHeight]);
        },
        createTooltip: function () {
            this.tooltip = d3
                .select(`#${this.divName}`)
                .append("div")
                .attr("id", `tooltip${this.id}`)
                .style("opacity", 0)
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("pointer-events", "none")
                .style("background-color", "black")
                .style("border-radius", "5px")
                .style("padding", "10px")
                .style("border", "2px solid white")
                .style("color", "white")
                .style("font-size", "10px");
        },
        makeSelectCircleStandOut: function (selectedData) {
            this.svg
                .selectAll("circle")
                .filter((d) => {
                    return d == selectedData;
                })
                .attr("fill", "red");
        },
        restoreCircleStyle: function () {
            this.svg.selectAll("circle").attr("fill", "black");
        },
        showTooltip: function (event, d) {
            this.makeSelectCircleStandOut(d);
            // switch to left or right
            let centerX = this.plotWidth / 2;
            let centerY = this.plotHeight / 2;
            let xCoord;
            let yCoord;
            // get x coord
            if (event.offsetX > centerX) {
                xCoord = event.offsetX - 6 * d.name.length;
            } else {
                xCoord = event.offsetX + 4 * d.name.length;
            }
            // get ycoord
            if (event.offsetY > centerY) {
                yCoord = event.offsetY - 40;
            } else {
                yCoord = event.offsetY + 20;
            }
            this.tooltip
                .style("opacity", 1)
                .html(`${d.name}`)
                .style("left", xCoord + "px")
                .style("top", yCoord + "px");
        },
        moveTooltip: function (event, d) {
            let centerX = this.plotWidth / 2;
            let centerY = this.plotHeight / 2;
            let xCoord;
            let yCoord;
            // get x coord
            if (event.offsetX > centerX) {
                xCoord = event.offsetX - 6 * d.name.length;
            } else {
                xCoord = event.offsetX + 4 * d.name.length;
            }
            // get ycoord
            if (event.offsetY > centerY) {
                yCoord = event.offsetY - 40;
            } else {
                yCoord = event.offsetY + 20;
            }
            this.tooltip
                .style("opacity", 1)
                .style("left", xCoord + "px")
                .style("top", yCoord + "px");
        },
        hideTooltip: function (e) {
            this.restoreCircleStyle();
            this.tooltip.transition().style("opacity", 0);
        },
        xAxisGenerator: function (args) {
            return d3
                .axisBottom(this.xScale)
                .tickFormat(this.xAxisFormatter)
                .tickSize(0)(args);
        },
        yAxisGenerator: function (args) {
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
            if (this.plotData.length < 5) {
                return val;
            }
            if (this.plotData.length < 10) {
                if (index % 2 == 0) {
                    return `Rank ${this.plotData.length - index}`;
                }
                return;
            }
            if (index % Math.floor(this.plotData.length / 5) == 0) {
                return `Rank ${this.plotData.length - index}`;
            }
            return;
        },
        createCircles: function () {
            /*
        creates bars of barchart and adds them to this.svg
      */
            this.svg
                .selectAll("circle")
                .data(this.plotData, key)
                .enter()
                .append("circle")
                .attr("r", (d) => {
                    if (d.value) {
                        return 7;
                    }
                    return 0;
                })
                .attr("cx", (d) => {
                    return this.xScale(d.name) + this.xScale.bandwidth() / 2;
                })
                .attr("fill", "black")
                .attr("cy", () => {
                    return this.plotHeight;
                })
                .transition()
                .delay((d) => {
                    return (
                        (this.xScale(d.name) / 150 / this.plotData.length) *
                        1000
                    );
                })
                .duration(500)
                .attr("cy", (d) => {
                    if (d.value) {
                        return this.plotHeight - this.yScale(d.value);
                    }
                    return 0;
                });
            // attach event handler
            this.svg
                .selectAll("circle")
                .on("mouseover", this.showTooltip)
                .on("mousemove", this.moveTooltip)
                .on("mouseleave", this.hideTooltip);
        },
        updateCircles: function () {
            /*
        Updates bar chart with new data
      */
            // put in new data and store selection
            let circles = this.svg.selectAll("circle").data(this.plotData, key);
            // remove old data
            circles
                .exit()
                .transition()
                .duration(500)
                .attr("cy", () => {
                    return this.plotHeight;
                })
                .remove();
            // add new ones
            circles
                .enter()
                .append("circle")
                .attr("cx", (d) => {
                    return this.xScale(d.name) + this.xScale.bandwidth() / 2;
                })
                .attr("fill", "black")
                .attr("r", (d) => {
                    if (d.value) {
                        return 7;
                    }
                    return 0;
                })
                .attr("cy", () => {
                    return this.plotHeight;
                })
                .transition()
                .delay((d) => {
                    return (
                        (this.xScale(d.name) / 150 / this.plotData.length) *
                        1000
                    );
                })
                .duration(500)
                .attr("cy", (d) => {
                    if (d.value) {
                        return this.plotHeight - this.yScale(d.value);
                    }
                    return 0;
                });
            // reposition old bars
            circles
                .transition()
                .duration(500)
                .attr("r", (d) => {
                    if (d.value) {
                        return 7;
                    }
                    return 0;
                })
                .attr("cx", (d) => {
                    return this.xScale(d.name) + this.xScale.bandwidth() / 2;
                })
                .attr("width", this.xScale.bandwidth())
                .attr("cy", (d) => {
                    if (d.value) {
                        return this.plotHeight - this.yScale(d.value);
                    }
                    return 0;
                });
            // attach event handler
            this.svg
                .selectAll("circle")
                .on("mouseover", this.showTooltip)
                .on("mousemove", this.moveTooltip)
                .on("mouseleave", this.hideTooltip);
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
            this.createTooltip();
            this.createCircles();
        },
    },
    mounted: function () {
        this.createScales();
        this.createChart();
    },
    watch: {
        height: function () {
            d3.select(`#${this.svgName}`).remove();
            d3.select(`#tooltip${this.id}`).remove();
            this.createScales();
            this.createChart();
        },
        width: function () {
            d3.select(`#${this.svgName}`).remove();
            d3.select(`#tooltip${this.id}`).remove();
            this.createScales();
            this.createChart();
        },
        rawData: function () {
            this.createScales();
            this.updateAxes();
            this.updateCircles();
        },
    },
};
</script>

<style>
.no-margin {
    margin: 0px;
}
</style>
