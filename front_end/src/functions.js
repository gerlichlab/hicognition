export function convert_json_to_pilingJS(jsonObject, log = false) {
    /*
    Converts pileup data from pandas.DataFrame.to_json to an
    object that pilingJS can read

    input Json: '{"variable":{...},"group":{...},"value":{...}}'
    output Object: [
      {
        data: [flattenedArrayOfData],
        shape: [rowNumber, colNumber],
        dtype: "datatype"
      }
    ]
  */
    var rowNumber = Math.max(...Object.values(jsonObject["variable"])) + 1;
    var colNumber = Math.max(...Object.values(jsonObject["group"])) + 1;
    var objectLength = Object.keys(jsonObject["variable"]).length;
    var data = [];
    for (var index = 0; index < objectLength; index++) {
        var newValue;
        if (log) {
            // first check whether value is undefined
            if (jsonObject["value"][index]) {
                newValue = Math.log2(jsonObject["value"][index]);
            } else {
                newValue = undefined;
            }
        } else {
            newValue = jsonObject["value"][index];
        }
        // check where in the data object value should be put
        var rowIndex = jsonObject["variable"][index];
        var colIndex = jsonObject["group"][index];
        var flattenedIndex = rowIndex * colNumber + colIndex;
        data[flattenedIndex] = newValue;
    }
    return [
        {
            src: {
                data: data,
                shape: [rowNumber, colNumber],
                dtype: "float32"
            }
        }
    ];
}

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
    for (var index = 0; index < numberDatasets; index++) {
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

export function group_stackups(data) {
    /*
  Takes as input an array of json objects that are returned by the averageIntervalData route (e.g.
 
  [{id:1, binsize:50000, value_type: "obs/exp"}...]
 
  and groups iccf and obs_exp per binsize such that the result is an object of the form
 
  {binsize: {iccf: averageIntervalData_id, Obs/Exp: averageIntervalData_id, binsize: 400000}, ...}
  FIXME: Probably this can be removed.
  */
    var numberDatasets = data.length;
    console.log(data);
    var output = {};
    for (var index = 0; index < numberDatasets; index++) {
        var { id, binsize } = data[index];
        var value_type = "normal";
        if (binsize in output) {
            // binsize is already in output, must be the other type of pileup
            output[binsize][value_type] = id;
        } else {
            // binsize is not in output, must be the first type of pileup
            output[binsize] = { binsize: binsize };
            output[binsize][value_type] = id;
        }
    }
    //console.log(output)
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
