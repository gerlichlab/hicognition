import * as d3 from "d3";

export function getScale(min, max, scaleType) {
    // returns a iccf color scale or obs/exp color scale with the specified
    // min, max values
    if (scaleType == "fall") {
        return d3
            .scaleLinear()
            .range(["white", "orange", "red", "black"])
            .domain(distributeMinMax(min, max));
    } else if (scaleType == "blueWhiteRed") {
        // check whether 0 is between min and max
        let midpoint = 0;
        if (min * max > 0) {
            midpoint = (min + max) / 2;
        }
        return d3
            .scaleDiverging(t => d3.interpolateRdBu(1 - t))
            .domain([min, midpoint, max]);
    } else if (scaleType == "plasma") {
        return d3.scaleSequential(d3.interpolatePlasma).domain([min, max]);
    } else if (scaleType == "magma") {
        return d3.scaleSequential(d3.interpolateMagma).domain([min, max]);
    } else if (scaleType == "viridis") {
        return d3.scaleSequential(d3.interpolateViridis).domain([min, max]);
    } else {
        // default is reds
        return d3.scaleSequential(d3.interpolateReds).domain([min, max]);
    }
}

function distributeMinMax(min, max) {
    /* calculates pivot values for d3.scaleLinear

         |Min-----Pivot1-----Pivot2-----Max|

        Min-Pivot1, Pivot1-Pivot2 and Pivot2-Max
        are all 1/3 of the total range
    */
    var range = max - min;
    return [min, min + range / 3, min + (2 * range) / 3, max];
}
