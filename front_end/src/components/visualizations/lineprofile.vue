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
            margin: { top: 10, right: 50, bottom: 0, left: 20 },
            svg: undefined,
            xScale: undefined,
            yScale: undefined,
            focus: undefined
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
        getValueFormat: function(val){
            if (!this.normalized){
                return val.toExponential(0)
            }
            return val
        },
        bisectData: d3.bisector(d => d.date).left,
        yAxisGenerator: function(args) {
            return d3
                .axisLeft(this.yScale)
                .tickFormat((val) => this.getValueFormat(val))
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
        handleMouseMove: function(event){
            this.svg.selectAll(".focus")
                .select(".lineHover")
                .attr("transform", "translate(" + d3.pointer(event)[0] + ",0)")
        },
        createHoverObjects: function(){
            // create overlay
            this.svg.append("rect")
                    .attr("class", "overlayRect")
                    .attr("x", this.margin.left)
                    .attr("width", this.width + this.margin.right + this.margin.left)
                    .attr("height", this.height)

            let focus = this.svg.append("g")
                .attr("class", "focus")
                .style("display", "none");

            focus.append("line").attr("class", "lineHover")
                .style("stroke", "#999")
                .attr("stroke-width", 2)
                .style("shape-rendering", "crispEdges")
                .style("opacity", 0.5)
                .attr("y1", this.height)
                .attr("y2",0);
            // register handlers on top level group
            this.svg
                .on("mouseover", function() { focus.style("display", null); })
                .on("mouseleave", function(e) {console.log(e); focus.style("display", "none")})
                .on("mousemove", this.handleMouseMove)
        },
        createScales: function(){
            let { minX, maxX, minY, maxY } = this.valueBoundaries;
            this.xScale = d3
                .scaleLinear()
                .domain([minX - 0.1 * (maxX - minX), maxX])
                .range([0, this.width]);
            this.yScale =  d3
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
            this.createHoverObjects()
        },
        createAxes: function() {
            this.svg
                .append("g")
                .attr("class", "y axis")
                .attr("transform", "translate(" + 2 + "0)")
                .call(this.yAxisGenerator);
        },
        addDataLine: function(single_data, color_index){
            this.svg
                    .append("path")
                    .attr("d", this.lineGenerator(single_data.data))
                    .attr("fill", "none")
                    .attr("stroke", d3.schemeDark2[color_index])
                    .attr("stroke-width", 1.5);
                this.svg
                    .append("text")
                    .attr(
                        "transform",
                        "translate(" +
                            (this.width - 40) +
                            "," +
                            (this.yScale(
                                single_data.data[single_data.data.length - 1]
                            ) +
                                10) +
                            ")"
                    )
                    .attr("dy", ".35em")
                    .attr("text-anchor", "start")
                    .style("font-size", "12px")
                    .style("fill", d3.schemeDark2[color_index])
                    .text(this.lineNames[color_index]);
        },
        drawLinechart: function() {
            this.createSVG();
            this.createScales()
            // add data
            var color_index = 0;
            for (let single_data of this.lineData) {
                this.addDataLine(single_data, color_index)
                color_index = color_index + 1;
            }
            // add axes
            this.createAxes();
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
