<template>
    <div :id="colorBarDivID" class="fillSpace"></div>
</template>

<script>
import * as d3 from "d3";

export default {
    name: "colorBarSlider",
    props: {
        sliderMin: Number,
        sliderMax: Number,
        sliderWidth: Number,
        sliderPositionMin: Number,
        sliderPositionMax: Number,
        colorMapName: String
    },
    data: function() {
        return {
            svg: undefined,
            id: Math.round(Math.random() * 100000),
            width: undefined,
            height: undefined,
            margin: { top: 10, right: 0, bottom: 10, left: 30 }
        };
    },
    computed: {
        colorBarDivID: function() {
            return `colorBar${this.id}`;
        },
        plotWidth: function(){
            return this.width - this.margin.left - this.margin.right
        },
        plotHeight: function(){
            return this.height - this.margin.top - this.margin.bottom
        }
    },
    methods: {
        getParentWidth: function() {
            return document.getElementById(this.colorBarDivID).parentNode
                .offsetWidth;
        },
        getParentHeight: function() {
            return document.getElementById(this.colorBarDivID).parentNode
                .offsetHeight;
        },
        createChart: function() {
            this.svg = d3
                .select(`#${this.colorBarDivID}`)
                .append("svg")
                .attr("id", `${this.colorBarDivID}Svg`)
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
        translateAxis: function(width) {
            var tX = width;
            var tY = 0;
            return tX + "," + tY;
        },
        colorbar: function(scale, width, height) {
            var tickValues = scale.domain(),
                axisGroup = null;
            var linearScale = d3
                .scaleLinear()
                .domain(scale.domain())
                .range([0, height]);
            var barThickness = width;
            var barRange = height;

            let colorbar = (context) => {
                var dL = 1;
                var nBars = Math.floor(barRange / dL);
                var barData = [];
                var trueDL = (barRange * 1) / nBars;
                for (var i = 0; i < nBars; i++) {
                    barData.push(i * trueDL);
                }

                var interScale = d3
                    .scaleLinear()
                    .domain([0, barRange])
                    .range(scale.domain());

                context
                    .selectAll("rect")
                    .data(barData)
                    .enter()
                    .append("rect")
                    .attr("x", translateX)
                    .attr("y", translateY)
                    .attr(
                        "width",
                        barThickness
                    )
                    .attr(
                        "height",
                        trueDL
                    )
                    .style("stroke-width", "0px")
                    .style("fill", function(d, i) {
                        return scale(interScale(d));
                    });

                var myAxis = d3.axisLeft(linearScale).ticks(3);
                if (tickValues == null) tickValues = myAxis.tickValues();
                else myAxis.tickValues(tickValues);
                axisGroup = context
                    .append("g")
                    .attr("class", "colorbar axis")
                    .attr(
                        "transform",
                        "translate(" +
                            0 + "," + 0 + 
                            ")"
                    )
                    .call(myAxis)
                    .selectAll(".tick")
                    .data(tickValues);
            }

            // set and return for chaining, or get
            colorbar.scale = function(_) {
                return arguments.length ? ((scale = _), colorbar) : scale;
            };

            colorbar.tickValues = function(_) {
                return arguments.length
                    ? ((tickValues = _), colorbar)
                    : tickValues;
            };

            function translateX(d, i) {
                return 0;
            }

            function translateY(d, i) {
                return d;
            }

            return colorbar;
        },
        attachColorbar: function(){
            var colorScale = d3.scaleSequential(d3.interpolateWarm).domain([-1,1]);
            var cb = this.colorbar(colorScale, this.plotWidth, this.plotHeight);
            this.svg.call(cb);
        }
    },
    mounted: function() {
        this.height = this.getParentHeight();
        this.width = this.getParentWidth();
        this.createChart();
        this.attachColorbar();
    }
};
</script>

<style>
.fillSpace {
    width: 100%;
    height: 100%;
}
</style>
