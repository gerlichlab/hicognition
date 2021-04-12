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

function range(start,end){
    var ans =[];
    for (let i =start; i<=end;i++){
        ans.push(i);
    }
    return ans
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
            return{
                y: this.lineprofileData.data,
                x: range(1,this.lineprofileData.data.length)
            };
        },
    },
    methods: {
        redrawLinechart: function() {
            var margin = { top: 10, right: 30, bottom: 30, left: 60 };
            console.log(this.lineData)
            d3.select(`#${this.lineprofileDivID}Svg`).remove();
            var svg = d3
                .select(`#${this.lineprofileDivID}Svg`)
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
            var x = d3
                .scaleLinear()
                .domain([1, 100])
                .range([0, this.width]);
            svg.append("g")
                .attr("transform", "translate(0," + this.height + ")")
                .call(d3.axisBottom(x));

            // Add Y axis
            var y = d3
                .scaleLinear()
                .domain([0, 13])
                .range([this.height, 0]);
            svg.append("g").call(d3.axisLeft(y));

            // Add the line
            svg.append("path")
                .datum(this.lineData)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 1.5)
                .attr(
                    "d",
                    d3
                        .line()
                        .x(function(d) {
                            return x(d.x);
                        })
                        .y(function(d) {
                            return y(d.y);
                        })
                );
        }
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
