import * as math from "mathjs";

const FLOATDIFFERENCE = 10 ** -8;


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
    if (array.length == 0){
        return undefined
    }
    var max = -Infinity;
    for (var val of array) {
        if (isFinite(val)) {
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
    if (array.length == 0){
        return undefined
    }
    var min = Infinity;
    for (var val of array) {
        if (isFinite(val)) {
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

export function normalizeLineProfile(lineProfile) {
    let max_value = max_array(lineProfile);
    let min_value = min_array(lineProfile);
    if (max_value - min_value < FLOATDIFFERENCE) {
        return lineProfile.map(val => {
            if (val && isFinite(val)) {
                return 1;
            }
            return undefined;
        });
    }
    return lineProfile.map(val => {
        if (val && isFinite(val)) {
            return (val - min_value) / (max_value - min_value);
        }
        return undefined;
    });
}

export function getPercentile(array, p) {
    /*
        Returns pth percentile of array
    */
   if ( (p < 0) || (p > 100)){
       return undefined
   }
    let cleaned_array = array.filter((val) => {
        return isFinite(val) && (val != null)
    })
    let sorted_array = cleaned_array.sort((a,b) => a - b);
    let index = Math.ceil(( (sorted_array.length -1) * p) / 100)
    return sorted_array[index];
}

export function getPerMilRank(array, p) {
    /*
        Returns pth percentile of array
    */
   if ( (p < 0) || (p > 1000)){
       return undefined
   }
    let cleaned_array = array.filter((val) => {
        return isFinite(val) && (val != null)
    })
    let sorted_array = cleaned_array.sort((a,b) => a - b);
    let index = Math.ceil(( (sorted_array.length -1) * p) / 1000)
    return sorted_array[index];
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
