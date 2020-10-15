import * as d3 from "d3";

export var iccfScale = d3.scaleLinear()
    .range(["white", "orange", "red", "black"])
    .domain([0, 6.6, 13.2, 20])

export function getScale(min, max, scaleType) {
    // returns a iccf color scale with the specified
    // min, max and pivot values
    if (scaleType == "ICCF"){
        return d3.scaleLinear()
                        .range(["white", "orange", "red" ,"black"])
                        .domain(distributeMinMax(min, max));
    }else{
        throw "Not Implemented!";
    }
}

function distributeMinMax(min, max) {
    /* calculates pivot values for d3.scaleLinear

         |Min-----Pivot1-----Pivot2-----Max|

        Min-Pivot1, Pivot1-Pivot2 and Pivot2-Max
        are all 1/3 of the total range
    */
   var range = max - min;
   return [min, min + range/3, min + 2*range/3, max]
}

