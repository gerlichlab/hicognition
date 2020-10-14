import * as d3 from "d3";

export var iccfScale = d3.scaleLinear()
    .range(["white", "orange", "red", "black"])
    .domain([0, 6.6, 13.2, 20])

