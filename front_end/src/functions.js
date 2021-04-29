import * as math from "mathjs";

const FLOATDIFFERENCE = 10**(-8)

export function convert_json_to_d3(jsonObject, log = false) {
    /*
      Converts pileup data from pandas.DataFrame.to_json to an 
      object that d3 can read

      input Json: '{"variable":{...},"group":{...},"value":{...}}'
      output object: [
          {
              variable: 0,
              group: 0,
              value: 1.23
          }
      ]
      Log2 is taken of output value if log is true.
  */
    var output = [];
    var objectLength = Object.keys(jsonObject["variable"]).length;
    for (var index = 0; index < objectLength; index++) {
        var newValue;
        if (log) {
            // first check whether value is undefined
            if (jsonObject["value"][index]) {
                newValue = Math.log2(jsonObject["value"][index]);
            } else {
                newValue = null;
            }
        } else {
            newValue = jsonObject["value"][index]; // undefined * number is NaN
        }

        // extract infos for current entry
        var currentEntry = {
            variable: jsonObject["variable"][index],
            group: jsonObject["group"][index],
            value: newValue
        };
        output.push(currentEntry);
    }
    return output;
}

export function group_iccf_obs_exp(data) {
    /*
  Takes as input an array of json objects that are returned by the averageIntervalData route (e.g.

  [{id:1, binsize:50000, value_type: "obs/exp"}...]

  and groups iccf and obs_exp per binsize such that the result is an object of the form

  {binsize: {iccf: averageIntervalData_id, Obs/Exp: averageIntervalData_id, binsize: 400000}, ...}
  
  The binsize key is duplicated for convenience because then iccf and obs/exp averageIntervalData
  can be selected by object[binsize] and when iterating over the result one can
  access binsize as item.binsize.
  )
  */
    var numberDatasets = data.length;
    var output = {};
    for (let index = 0; index < numberDatasets; index++) {
        var { id, binsize, value_type } = data[index];
        if (binsize in output) {
            // binsize is already in output, must be the other type of pileup
            output[binsize][value_type] = id;
        } else {
            // binsize is not in output, must be the first type of pileup
            output[binsize] = { binsize: binsize };
            output[binsize][value_type] = id;
        }
    }
    return output;
}

export function group_stackups_by_binsize(data) {
    /*
  Takes as input an array of json objects of the form [{"binsize": x, "id", y}]
  and groups them by binsize into an output object: {binsize: {binsize: x, id, y}}
  */
    var numberDatasets = data.length;
    var output = {};
    for (let index = 0; index < numberDatasets; index++) {
        var binsize = data[index]["binsize"];
        output[binsize] = {};
        output[binsize]["binsize"] = binsize;
        output[binsize]["id"] = data[index]["id"];
    }
    return output;
}

// TODO: group_lineprofils_by_binsizeprofils
export function group_lineprofils_by_binsize(data, intersection = true) {
    /*
  Takes as input an array of json objects of the form [{"binsize": x, "id", y1}{"binsize": x, "id", y2}]
  and groups them by binsize into an output object: {binsize: {binsize: x, id, {y1,y2}}}
  */

    var output = {};
    for (let interval of data) {
        var binsize = interval.binsize;
        if (binsize in output) {
            output[binsize]["id"].push(interval.id);
        } else {
            output[binsize] = { binsize: binsize, id: [] };
            output[binsize]["id"].push(interval.id);
        }
    }
    if (intersection == true) {
        //TODO Remove binsizes where there is no intersection.
        //console.log("Intersection Tested")
    }
    return output;
}

export function group_intervals_on_windowsize(intervals) {
    /*
    data is array intervals object [{"id": 1, "windowsize": 20000, ...}]
    transform data from [{"id", "windowsize"}, ...] to {"windwosize: {"windowsize": 200000, id: [id1, id2,....]}, ...]
  */
    var output = {};
    for (var interval of intervals) {
        var windowsize = interval.windowsize;
        if (windowsize in output) {
            output[windowsize]["id"].push(interval.id);
        } else {
            output[windowsize] = { windowsize: windowsize, id: [] };
            output[windowsize]["id"].push(interval.id);
        }
    }
    return output;
}

export function argsort(sort_values, ascending = true) {
    if (ascending) {
        return Array.from(Array(sort_values.length).keys()).sort((a, b) =>
            sort_values[a] < sort_values[b]
                ? -1
                : (sort_values[b] < sort_values[a]) | 0
        );
    } else {
        return Array.from(Array(sort_values.length).keys()).sort((a, b) =>
            sort_values[a] > sort_values[b]
                ? -1
                : (sort_values[b] > sort_values[a]) | 0
        );
    }
}

export function sort_matrix_by_index(
    flattened_matrix,
    shape,
    sort_values,
    ascending = true
) {
    /*
        Takes a flattened_matrix of shape [width, height] and sorts it
        along the first dimension by the passed sort_values either ascending
        or descending.
    */
    // prepare matrix
    var reshaped = math.reshape(flattened_matrix, shape);
    // sort_values and return sort indices
    var sort_indices = argsort(sort_values, ascending);
    var sorted = math.subset(
        reshaped,
        math.index(sort_indices, [...Array(shape[1]).keys()])
    );
    return math.flatten(sorted);
}

export function max_array(array) {
    /*
        returns maximum element of array
    */
    var max = 0;
    for (var val of array) {
        if (val && isFinite(val)) {
            if (val > max) {
                max = val;
            }
        }
    }
    return max;
}

export function min_array(array) {
    /*
        returns minimum element of array
    */
    var min = Infinity;
    for (var val of array) {
        if (val && isFinite(val)) {
            if (val < min) {
                min = val;
            }
        }
    }
    return min;
}

export function sort_matrix_by_center_column(
    flattened_matrix,
    shape,
    ascending = false
) {
    /*
        Takes a flattened_matrix of shape [width, height] and sorts it based on its center column either ascending
        or descending.
    */
    // prepare matrix
    var reshaped = math.reshape(flattened_matrix, shape);
    // center column
    var sort_values = math.flatten(
        math.subset(
            reshaped,
            math.index([...Array(shape[0]).keys()], Math.floor(shape[1] / 2))
        )
    );
    return sort_matrix_by_index(
        flattened_matrix,
        shape,
        sort_values,
        ascending
    );
}

export function normalizeLineProfile(lineProfile){
    let max_value = max_array(lineProfile);
    let min_value = min_array(lineProfile);
    if ((max_value - min_value) < FLOATDIFFERENCE){
        return lineProfile.map((val) => {
            if (val && isFinite(val)){
                return 1
            }
            return undefined
        })
    }
    return lineProfile.map((val) => {
        if (val && isFinite(val)){
            return (val - min_value)/(max_value - min_value)
        }
        return undefined
    })
}

// Helpers for datasetTable

export function toLower(text) {
    return text.toString().toLowerCase();
}

export function searchByName(items, term) {
    /*
  helper to search table fields by name for datasetTable
  */
    if (term) {
        var filtered_items = items.filter(item => {
            return toLower(item.dataset_name).includes(toLower(term));
        });
        return filtered_items;
    }

    return items;
}
