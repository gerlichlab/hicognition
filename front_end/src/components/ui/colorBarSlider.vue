<template>
    <div :id="colorBarDivID" :style="colorBarDivStyle"></div>
</template>

<script>
import * as d3 from "d3";
import { getScale } from "../../colorScales.js";

export default {
    name: "colorBarSlider",
    props: {
        sliderMin: Number,
        sliderMax: Number,
        heatMapWidth: Number, // this is only passed to check when the parent resizes, value is not actually used
        sliderPositionMin: Number,
        sliderPositionMax: Number,
        colormap: String,
        borderColor: String,
        borderStyle: String
    },
    data: function() {
        return {
            svg: undefined,
            id: Math.round(Math.random() * 100000),
            width: undefined,
            height: undefined,
        };
    },
    computed: {
        margin: function(){
            return {
                top: this.height * 0.05,
                right: this.width * 0.1,
                bottom: this.height * 0.05,
                left: this.width * 0.7
            }
        },
        colorBarDivID: function() {
            return `colorBar${this.id}`;
        },
        colorBarDivStyle: function(){
            let borderStyle = this.borderStyle ? this.borderStyle : "none"
            return {
                width: "100%",
                height: "100%",
                "box-sizing": "border-box",
                "border-style": `none none none ${borderStyle}`,
                "border-width": "3px",
                "border-color": this.borderColor
                    ? this.borderColor
                    : "none"
            }
        },
        plotWidth: function(){
            return this.width - this.margin.left - this.margin.right
        },
        plotHeight: function(){
            return this.height - this.margin.top - this.margin.bottom
        },
        colorScale: function(){
            return getScale(this.sliderPositionMin, this.sliderPositionMax, this.colormap);
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
        dragStopEventHandler: function(event){

        },
        createChart: function() {
            d3.select(`#${this.colorBarDivID}Svg`).remove();
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
            // attach colorbar
            this.attachColorbar()
                
        },
        colorbar: function(scale, width, height, scale_start, scale_end) {
            let scale_domain = scale.domain()
            let initialMin = scale_domain[0]
            let initialMax = scale_domain[scale_domain.length - 1]
            var linearScale = d3
                .scaleLinear()
                .domain([scale_start, scale_end])
                .range([height, 0]);
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
                    .domain([barRange, 0])
                    .range([scale_start, scale_end]);

                // attach gradient rectangles
                context
                    .selectAll("rect")
                    .data(barData)
                    .enter()
                    .append("rect")
                    .attr("x", 0)
                    .attr("y", (d) => d)
                    .attr(
                        "width",
                        barThickness
                    )
                    .attr(
                        "height",
                        trueDL
                    )
                    .style("stroke-width", "0px")
                    .style("fill", function(d) {
                        if ((interScale(d) < initialMin) || (interScale(d) > initialMax)){
                            return "rgba(120,120,120, 0.1)"
                        }
                        return scale(interScale(d));
                    });

                // needs to be defined here because if it is a vue methods this gets everridden; store
                let dragEventHandler = function(event){
                    // check whether y position is allowed
                    if ((event.y > 0) && (event.y < barRange)){
                        // adjust y position
                        d3.select(this)
                            .attr("y", event.y)
                    }
                }
                let component = this
                let dragStopEventHandler = function(event){
                    // add boundaries for trying to drag further
                    let y_value = event.y
                    if (y_value < 0){
                        y_value = 0
                    }
                    if (y_value > barRange){
                        y_value = barRange
                    }
                    let event_value = interScale(y_value)
                    if (this.id == "upper"){
                        if (event_value < component.sliderPositionMin){
                            component.$emit("slider-change", [event_value, component.sliderPositionMin]);
                        }else{
                            component.$emit("slider-change", [component.sliderPositionMin, event_value]);
                        }
                    }else{
                        if (event_value > component.sliderPositionMax){
                            component.$emit("slider-change", [component.sliderPositionMax, event_value, ]);
                        }else{
                            component.$emit("slider-change", [event_value, component.sliderPositionMax]);
                        }
                    }
                }
                let drag = d3.drag();
                drag.on("drag", dragEventHandler);
                drag.on("end", dragStopEventHandler)
                                    

                // attach colorbar slider rectangles
                context
                    .selectAll("colorSlider")
                    .data([initialMin])
                    .enter()
                    .append("rect")
                    .attr("id", "lower")
                    .attr("x", 0)
                    .attr("y", (d) => linearScale(d))
                    .attr("width", barThickness + this.width * 0.1)
                    .attr("height", this.width * 0.1)
                    .style("fill", "black")
                    .call(drag)
                
                context
                    .selectAll("colorSlider")
                    .data([initialMax])
                    .enter()
                    .append("rect")
                    .attr("id", "upper")
                    .attr("x", 0)
                    .attr("y", (d) => linearScale(d))
                    .attr("width", barThickness + this.width * 0.1)
                    .attr("height", this.width * 0.1)
                    .style("fill", "black")
                    .call(drag)


                var myAxis = d3.axisLeft(linearScale).ticks(5);
                context
                    .append("g")
                    .attr("class", "colorbar axis")
                    .attr(
                        "transform",
                        "translate(" +
                            0 + "," + 0 + 
                            ")"
                    )
                    .call(myAxis)
            }

            return colorbar;
        },
        attachColorbar: function(){
            var cb = this.colorbar(this.colorScale, this.plotWidth, this.plotHeight, this.sliderMin, this.sliderMax);
            this.svg.call(cb);
        }
    },
    mounted: function() {
        this.height = this.getParentHeight();
        this.width = this.getParentWidth();
        this.createChart();
    },
    watch: {
        colormap: function(){
            this.createChart()
        },
        sliderMax: function(){
            this.createChart()
        },
        sliderMin: function(){
            this.createChart()
        },
        sliderPositionMin: function(){
            this.createChart()
        },
        sliderPositionMax: function(){
            this.createChart()
        },
        heatMapWidth: function(){
            this.height = this.getParentHeight();
            this.width = this.getParentWidth();
            this.createChart()
        }
    }
};
</script>

<style>
.fillSpace {
    width: 100%;
    height: 100%;
}
</style>
