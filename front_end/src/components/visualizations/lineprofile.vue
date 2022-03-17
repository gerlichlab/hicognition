<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <div :id="lineprofileDivID" class="small-margin" :style="divStyle"/>
            </md-list-item>
        </md-list>
    </div>
</template>
<script>
import * as d3 from "d3";
import { min_array, max_array, normalizeLineProfile } from "../../functions";

const EXPANSION_FACTOR = 0.2;

export default {
    name: "lineprofile",
    props: {
        title: String,
        lineprofileData: Array,
        lineprofileNames: Array,
        normalized: Boolean,
        width: Number,
        height: Number,
        valueScaleColor: String,
        valueScaleBorder: String,
        minValueRange: Number,
        maxValueRange: Number,
        lineprofileID: Number, // lineprofile ID is needed because I am accessing the div of the lineprofile via id and they must be different for different pilups
        showInterval: {
            //  whehter to show interval start and end on x axis
            type: Boolean,
            default: false
        }
    },
    data: function() {
        return {
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            focus: undefined,
            colorMapping: new Map()
        };
    },
    computed: {
        margin: function() {
            return {
                top: this.height * 0.01,
                bottom: this.showInterval
                    ? this.height * 0.03
                    : this.height * 0.01,
                left: this.width * 0.14,
                right: this.width * 0.1
            };
        },
        divStyle: function(){
            let borderStyle = this.valueScaleBorder ? this.valueScaleBorder : "solid"
            return {
                width: "100%",
                height: "100%",
                "box-sizing": "border-box",
                "border-style": `none none none ${borderStyle}`,
                "border-width": "3px",
                "border-color": this.valueScaleColor
                    ? this.valueScaleColor
                    : "white"
            }
        },
        intervalStartBin: function() {
            if (this.lineData && this.lineData.length != 0) {
                let intervalSize = Math.round(
                    this.lineData[0].data.length / (1 + 2 * EXPANSION_FACTOR)
                );
                return Math.round(intervalSize * EXPANSION_FACTOR);
            }
            return undefined;
        },
        intervalEndBin: function() {
            if (this.lineData && this.lineData.length != 0) {
                let intervalSize = Math.round(
                    this.lineData[0].data.length / (1 + 2 * EXPANSION_FACTOR)
                );
                return (
                    intervalSize + Math.round(intervalSize * EXPANSION_FACTOR)
                );
            }
            return undefined;
        },
        fontSize: function() {
            let additionalSize = Math.floor((this.width - 350) / 50);
            let fontSize = 10 + additionalSize * 2;
            return `${fontSize}px`;
        },
        strokeWidth: function() {
            let additionalSize = Math.floor((this.width - 350) / 50);
            return 2 + 0.5 * additionalSize;
        },
        lineprofileDivID: function() {
            // ID for the div containing the lineprofile
            return "lineprofile_" + this.lineprofileID;
        },
        plotWidth: function() {
            return this.width - this.margin.left - this.margin.right;
        },
        plotHeight: function() {
            return this.height - this.margin.top - this.margin.bottom;
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
        getXaxisFormat: function(val) {
            if (val == this.intervalStartBin) {
                return "Start";
            }
            if (val == this.intervalEndBin) {
                return "End";
            }
            return undefined;
        },
        formatLabel: function(label) {
            if (label.length > 10) {
                return label.slice(0, 10) + "...";
            }
            return label;
        },
        xAxisGenerator: function(args) {
            return d3
                .axisBottom(this.xScale)
                .tickFormat(val => this.getXaxisFormat(val))
                .tickValues([this.intervalStartBin, this.intervalEndBin])(args);
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
                        this.plotHeight / 2.5 +
                        ")"
                )
                .text(e => {
                    return `${this.formatValue(
                        this.getValueFromIndex(index, e)
                    )} | ${this.formatLabel(e)}`;
                });
            // flip text around
            this.xScale(index) > this.plotWidth - this.plotWidth / 2
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
                .attr("width", this.plotWidth - 10)
                .attr("height", this.plotHeight);
            // create line
            let focus = this.svg
                .append("g")
                .attr("class", "focus")
                .style("display", "none");
            focus
                .append("line")
                .attr("class", "lineHover")
                .style("stroke", "#999")
                .attr("stroke-width", this.strokeWidth)
                .style("shape-rendering", "crispEdges")
                .style("opacity", 0.5)
                .attr("y1", this.plotHeight)
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
                .attr("font-size", this.fontSize * 1.4)
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
                .attr("r", this.strokeWidth * 3)
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
        createValueBoundaries: function() {
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
            this.$emit("value-scale-change", [0, 0, minY, maxY])
            if (
                this.minValueRange !== undefined &&
                this.maxValueRange !== undefined
            ) {
                return {
                    minX: minX,
                    maxX: maxX,
                    minY: this.minValueRange,
                    maxY: this.maxValueRange
                };
            }
            return {
                minX: minX,
                maxX: maxX,
                minY: minY,
                maxY: maxY
            };
        },
        createScales: function() {
            let { minX, maxX, minY, maxY } = this.createValueBoundaries();
            this.xScale = d3
                .scaleLinear()
                .domain([minX, maxX])
                .range([0, this.plotWidth]);
            this.yScale = d3
                .scaleLinear()
                .domain([minY - 0.05 * (maxY - minY), maxY])
                .range([this.plotHeight, 0]);
        },
        createSVG: function() {
            d3.select(`#${this.lineprofileDivID}Svg`).remove();
            this.svg = d3
                .select(`#${this.lineprofileDivID}`)
                .append("svg")
                .attr("id", `${this.lineprofileDivID}Svg`)
                .style("overflow", "visible") // needed for when tooltip goes over borders of svg
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
        },
        createAxes: function() {
            this.svg
                .append("g")
                .attr("class", "y axis")
                .call(this.yAxisGenerator);
            // set font-size
            if (this.showInterval) {
                this.svg
                    .append("g")
                    .attr("class", "x axis")
                    .attr("transform", `translate(0, ${this.plotHeight})`)
                    .call(this.xAxisGenerator);
            }
            this.svg.selectAll("text").style("font-size", this.fontSize);
        },
        addDataLine: function(single_data, color_index) {
            this.svg
                .append("path")
                .attr("d", this.lineGenerator(single_data.data))
                .attr("fill", "none")
                .attr("stroke", d3.schemeDark2[color_index])
                .attr("stroke-width", this.strokeWidth);
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
        minValueRange: function(){
            this.drawLinechart()
        },
        maxValueRange: function() {
            this.drawLinechart()
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

.small-margin {
    margin: 3px;
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
