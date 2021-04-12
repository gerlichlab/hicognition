<template>
    <div>
        <md-list class="md-double-line">
            <md-list-item class="md-alignment-top-center">
                <!-- Pileup display -->
                <md-content class="center-horizontal md-elevation-1">
                    <div :id="lineprofileDivID" class="small-margin" />
                </md-content>
            </md-list-item>
        </md-list>
    </div>
</template>
<script>
import * as d3 from "d3";

function range(start, end) {
    var ans = [];
    for (let i = start; i <= end; i++) {
        ans.push(i);
    }
    return ans;
}

export default {
    name: "lineprofile",
    props: {
        title: String,
        lineprofileData: Object,
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
            return {
                y: this.lineprofileData.data,
                x: range(1, this.lineprofileData.data.length)
            };
        }
    },
    methods: {
        redrawLinechart: function() {
            var margin = { top: 10, right: 30, bottom: 30, left: 30 };
            console.log(this.lineData.y);
            //console.log(Math.max.apply(Math, this.lineData.y));
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

            let minX = d3.min(this.lineData.x);
            let maxX = d3.max(this.lineData.x);
            let minY = d3.min(this.lineData.y);
            let maxY = d3.max(this.lineData.y);

            var x = d3
                .scaleLinear()
                .domain([minX, maxX])
                .range([0, this.width]);
            var y = d3
                .scaleLinear()
                .domain([minY-0.05*maxY, maxY])
                .range([this.height, 0]);
            let x_test = this.lineData.x;
            let y_test = this.lineData.y;
            var line = d3
                .line()
                .x(function(d, i) {
                    return x(x_test[i]);
                })
                .y(function(d, i) {
                    return y(y_test[i]);
                });
            // var x = d3
            //     .scaleLinear()
            //     .domain([0, this.lineprofileData.data.length])
            //     .range([0, this.width]);
            // svg.append("g")
            //     .attr("transform", "translate(0," + this.height + ")")
            //     .call(d3.axisBottom(x));

            // Add Y axis
            // var y = d3
            //     .scaleLinear()
            //     // ... is the short version for Math.max.apply(Math, this.lineData.y)
            //     .domain([0, Math.max(...this.lineData.y)])
            //     .range([this.height, 0]);
            // svg.append("g").call(d3.axisLeft(y));

            let g = line_svg.append("g");
            var xAxis = d3.axisBottom().scale(x);
            g.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + this.height + ")")
                .call(xAxis);

            var yAxis = d3.axisLeft().scale(y);
            g.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0,0)")
                .call(yAxis);

            g.append("path")
                .attr("d", line(this.lineData.x))
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 1.5);

            // var line = d3.svg
            //     .line()
            //     .x(function(d, i) {
            //         return x(d.x[i]);
            //     })
            //     .y(function(d, i) {
            //         return y(d.y[i]);
            //     });

            // Add the line
            // svg.append("path")
            //     .datum(this.lineData)
            //     .attr("fill", "none")
            //     .attr("stroke", "steelblue")
            //     .attr("stroke-width", 1.5)
            //     .attr(
            //         "d",
            //         d3
            //             .line()
            //             .x(function(d, i) {
            //                 return x(d.x[i]);
            //             })
            //             .y(function(d, i) {
            //                 return y(d.y[i]);
            //             })
            //     );
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
        lineprofileData: function() {
            this.redrawLinechart();
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
