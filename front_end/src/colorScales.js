import * as d3 from "d3";
import {
  interpolateOrRd,
  interpolateRdPu,
  interpolateRdBu
} from 'd3-scale-chromatic';

export function getScale(min, max, scaleType) {
    // returns a iccf color scale or obs/exp color scale with the specified
    // min, max values
    if (scaleType == "ICCF"){
        return d3.scaleLinear()
                        .range(["white", "orange", "red" ,"black"])
                        .domain(distributeMinMax(min, max));
    }else{
        return d3.scaleDiverging(t => d3.interpolateRdBu(1 - t))
                          .domain([min, 0, max])
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

// these functions are from https://github.com/flekschas/piling.js/blob/master/examples/matrices.js

const rgbStr2rgba = (rgbStr, alpha = 1) => {
  return [
    ...rgbStr
      .match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/)
      .slice(1, 4)
      .map((x) => parseInt(x, 10) / 256),
    alpha,
  ];
};

export function createColorMap (interpolator, numColors = 512) {
  let interpolatorFn;
  let invert;

  switch (interpolator) {
    case 'ICCF':
      interpolatorFn = interpolateOrRd;
      invert = false;
      break;

    case "ObsExp":
        interpolatorFn = interpolateRdBu;
        invert = true;
        break

    case 'purple':
    default:
      interpolatorFn = interpolateRdPu;
      break;
  }

  const colorMap = new Array(numColors)
    .fill(0)
    .map((x, i) =>
      rgbStr2rgba(
        interpolatorFn(Math.abs((invert * numColors - i) / numColors))
      )
    );

  colorMap[0] = [0, 0, 0, 0]; // Transparent

  return colorMap;
};
