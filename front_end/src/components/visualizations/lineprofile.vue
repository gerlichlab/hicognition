<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <md-content class="center-horizontal md-elevation-0">
                    <div :id="lineprofileDivID" class="small-margin" />
                </md-content>
            </md-list-item>
        </md-list>
    </div>
</template>
<script>
import * as d3 from "d3";
import { min_array, max_array, normalizeLineProfile } from "../../functions";

export default {
    name: "lineprofile",
    props: {
        title: String,
        lineprofileData: Array,
        lineprofileNames: Array,
        normalized: Boolean,
        width: Number,
        height: Number,
        lineprofileID: Number, // lineprofile ID is needed because I am accessing the div of the lineprofile via id and they must be different for different pilups
        log: Boolean
    },
    data: function() {
        return {
            margin: { top: 10, right: 10, bottom: 5, left: 40 },
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            focus: undefined,
            colorMapping: new Map()
        };
    },
    computed: {
        lineprofileDivID: function() {
            // ID for the div containing the lineprofile
            return "lineprofile_" + this.lineprofileID;
        },
        lineData: function() {
            if (this.normalized) {
                return this.lineprofileData.map(elem => {
                    return {
                        data: normalizeLineProfile(elem.data),
                        shape: elem.shape,
                        dtype: elem.dtype
                    };
                });
            }
            return this.lineprofileData;
        },
        lineNames: function() {
            return this.lineprofileNames;
        },
        valueBoundaries: function() {
            var minX = 0;
            var maxX = undefined;
            var minY = undefined;
            var maxY = undefined;
            for (let single_data of this.lineData) {
                if (maxX == undefined || maxX < single_data.data.length) {
                    maxX = single_data.data.length;
                }
                if (minY == undefined || minY > min_array(single_data.data)) {
                    minY = min_array(single_data.data);
                }
                if (maxY == undefined || maxY < max_array(single_data.data)) {
                    maxY = max_array(single_data.data);
                }
            }
            return {
                minX: minX,
                maxX: maxX,
                minY: minY,
                maxY: maxY
            };
        }
    },
    methods: {
        getValueFromIndex: function(val_index, val_name) {
            let val_array_index = this.lineprofileNames.indexOf(val_name);
            return this.lineData[val_array_index]["data"][val_index];
        },
        formatValue: function(value) {
            if (!this.normalized) {
                return value.toExponential(2);
            }
            return Math.round(value * 100) / 100;
        },
        getValueFormat: function(val) {
            if (!this.normalized) {
                return val.toExponential(2);
            }
            return val;
        },
        formatLabel: function(label){
            if (label.length > 10){
                return label.slice(0, 10) + "..."
            }
            return label
        },
        yAxisGenerator: function(args) {
            return d3
                .axisLeft(this.yScale)
                .tickFormat(val => this.getValueFormat(val))
                .ticks(5)(args);
        },
        lineGenerator: function(args) {
            return d3
                .line()
                .x((d, i) => {
                    return this.xScale(i);
                })
                .y((d, i) => {
                    return this.yScale(d);
                })(args);
        },
        handleMouseMove: function(event) {
            let focus = this.svg.selectAll(".focus");
            let index = Math.floor(this.xScale.invert(d3.pointer(event)[0]));
            focus
                .select(".lineHover")
                .attr("transform", "translate(" + this.xScale(index) + ",0)");
            // update circles
            focus
                .selectAll(".hoverCircle")
                .attr("cy", e => this.yScale(this.getValueFromIndex(index, e)))
                .attr("cx", this.xScale(index));
            // update text
            focus
                .selectAll(".lineHoverText")
                .attr(
                    "transform",
                    "translate(" +
                        d3.pointer(event)[0] +
                        "," +
                        this.height / 2.5 +
                        ")"
                )
                .text(e => {
                    return `${this.formatValue(
                        this.getValueFromIndex(index, e)
                    )} | ${this.formatLabel(e)}`;
                });
            // flip text around
            this.xScale(index) > this.width - this.width / 2
                ? focus
                      .selectAll("text.lineHoverText")
                      .attr("text-anchor", "end")
                      .attr("dx", -10)
                : focus
                      .selectAll("text.lineHoverText")
                      .attr("text-anchor", "start")
                      .attr("dx", 10);
        },
        createHoverObjects: function() {
            // create overlay
            this.svg
                .append("rect")
                .attr("class", "overlayRect")
                .attr("x", 5)
                .attr("width", this.width - 10)
                .attr("height", this.height);
            // create line
            let focus = this.svg
                .append("g")
                .attr("class", "focus")
                .style("display", "none");
            focus
                .append("line")
                .attr("class", "lineHover")
                .style("stroke", "#999")
                .attr("stroke-width", 2)
                .style("shape-rendering", "crispEdges")
                .style("opacity", 0.5)
                .attr("y1", this.height)
                .attr("y2", 0);
            // add labels
            var labels = focus
                .selectAll(".lineHoverText")
                .data(this.lineprofileNames);
            // add text labels
            labels
                .enter()
                .append("text")
                .attr("class", "lineHoverText")
                .style("fill", d => {
                    return this.colorMapping.get(d);
                })
                .attr("text-anchor", "start")
                .attr("font-size", 14)
                .attr("dy", (_, i) => 1 + i * 2 + "em")
                .merge(labels);
            // add circles
            var circles = focus
                .selectAll(".hoverCircle")
                .data(this.lineprofileNames);
            circles
                .enter()
                .append("circle")
                .attr("class", "hoverCircle")
                .style("fill", d => {
                    return this.colorMapping.get(d);
                })
                .attr("r", 6)
                .merge(circles);
            // register handlers on top level group
            this.svg
                .selectAll(".overlayRect")
                .on("mouseover", function() {
                    focus.style("display", null);
                })
                .on("mousemove", this.handleMouseMove);
            // mouseleave is on the group of data -> otherwise moving on rect will trigger mouseleave continuously
            this.svg.on("mouseleave", function() {
                focus.style("display", "none");
            });
        },
        createScales: function() {
            let { minX, maxX, minY, maxY } = this.valueBoundaries;
            this.xScale = d3
                .scaleLinear()
                .domain([minX, maxX])
                .range([0, this.width]);
            this.yScale = d3
                .scaleLinear()
                .domain([minY - 0.05 * (maxY - minY), maxY])
                .range([this.height, 0]);
        },
        createSVG: function() {
            d3.select(`#${this.lineprofileDivID}Svg`).remove();
            this.svg = d3
                .select(`#${this.lineprofileDivID}`)
                .append("svg")
                .attr("id", `${this.lineprofileDivID}Svg`)
                .style("overflow", "visible") // needed for when tooltip goes over borders of svg
                .attr(
                    "width",
                    this.width + this.margin.left + this.margin.right
                )
                .attr(
                    "height",
                    this.height + this.margin.top + this.margin.bottom
                )
                .append("g")
                .attr(
                    "transform",
                    "translate(" +
                        this.margin.left +
                        "," +
                        this.margin.top +
                        ")"
                );
        },
        createAxes: function() {
            this.svg
                .append("g")
                .attr("class", "y axis")
                .call(this.yAxisGenerator);
        },
        addDataLine: function(single_data, color_index) {
            this.svg
                .append("path")
                .attr("d", this.lineGenerator(single_data.data))
                .attr("fill", "none")
                .attr("stroke", d3.schemeDark2[color_index])
                .attr("stroke-width", 2);
            this.colorMapping.set(
                this.lineNames[color_index],
                d3.schemeDark2[color_index]
            );
        },
        drawLinechart: function() {
            this.createSVG();
            this.createScales();
            // add data
            let color_index = 0;
            for (let single_data of this.lineData) {
                this.addDataLine(single_data, color_index);
                color_index = color_index + 1;
            }
            // add axes
            this.createAxes();
            // add hover objects
            this.createHoverObjects();
        }
    },
    mounted: function() {
        this.drawLinechart();
    },
    watch: {
        height: function() {
            this.drawLinechart();
        },
        width: function() {
            this.drawLinechart();
        },
        lineData: {
            deep: true,
            handler() {
                this.drawLinechart();
            }
        }
    }
};
</script>

<style lang="scss">
.lineHoverText {
    text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, -2px 2px 0 #fff,
        2px 2px 0 #fff;
}

.center-horizontal {
    margin: auto;
    display: block;
}
.small-margin {
    margin: 5px;
}

.axis path {
    stroke-width: 2px;
}

.axis line {
    shape-rendering: crispEdges;
    stroke-width: 2px;
}

.overlayRect {
    fill: none;
    pointer-events: all;
}
</style>
