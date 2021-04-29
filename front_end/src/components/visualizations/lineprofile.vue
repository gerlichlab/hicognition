<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <!-- Pileup display -->
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
    computed: {
        lineprofileDivID: function() {
            // ID for the div containing the lineprofile
            return "lineprofile_" + this.lineprofileID;
        },
        lineData: function() {
            if (this.normalized){
                return this.lineprofileData.map((elem) => {
                    return {
                        data: normalizeLineProfile(elem.data),
                        shape: elem.shape,
                        dtype: elem.dtype
                    }
                });
            }
            return this.lineprofileData
        },
        lineNames: function() {
            return this.lineprofileNames;
        }
    },
    methods: {
        redrawLinechart: function() {
            var margin = { top: 10, right: 30, bottom: 20, left: 30 };
            d3.select(`#${this.lineprofileDivID}Svg`).remove();
            var line_svg = d3
                .select(`#${this.lineprofileDivID}`)
                .append("svg")
                .attr("id", `${this.lineprofileDivID}Svg`)
                .attr("width", this.width + margin.left + margin.right)
                .attr("height", this.height + margin.top + margin.bottom)
                .append("g")
                .attr(
                    "transform",
                    "translate(" + margin.left + "," + margin.top + ")"
                );
            // Add X axis
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

            var x = d3
                .scaleLinear()
                .domain([minX - 0.1 * (maxX - minX), maxX])
                .range([0, this.width]);
            var y = d3
                .scaleLinear()
                .domain([minY - 0.05 * (maxY - minY), maxY])
                .range([this.height, 0]);
            var line = d3
                .line()
                .x(function(d, i) {
                    return x(i);
                })
                .y(function(d, i) {
                    return y(d);
                });

            let g = line_svg.append("g");
            var xAxis = d3.axisBottom().scale(x);
            // g.append("g")
            //     .attr("class", "axis")
            //     .attr("transform", "translate(0," + this.height + ")")
            //     .call(xAxis);

            var yAxis = d3.axisLeft().scale(y);
            g.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0,0)")
                .call(yAxis);
            var color_index = 0;
            for (let single_data of this.lineData) {
                //console.log(single_data)
                g.append("path")
                    .attr("d", line(single_data.data))
                    .attr("fill", "none")
                    .attr("stroke", d3.schemeDark2[color_index])
                    .attr("stroke-width", 1.5);
                g.append("text")
                    .attr(
                        "transform",
                        "translate(" + (this.width - 40) + "," + (y(single_data.data[single_data.data.length - 1])+10) + ")"
                    )
                    .attr("dy", ".35em")
                    .attr("text-anchor", "start")
                    .style("font-size", "12px")
                    .style("fill", d3.schemeDark2[color_index])
                    .text(this.lineNames[color_index]);
                color_index = color_index + 1;
            }
        }
    },
    mounted: function() {
        this.redrawLinechart();
    },
    watch: {
        height: function() {
            this.redrawLinechart();
        },
        width: function() {
            this.redrawLinechart();
        },
        lineData: {
            deep: true,
            handler() {
                this.redrawLinechart();
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.center-horizontal {
    margin: auto;
    display: block;
}
.small-margin {
    margin: 5px;
}
</style>
