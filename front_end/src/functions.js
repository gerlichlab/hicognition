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

export function group_stackups_by_binsize(data) {
    /*
  Takes as input an array of json objects of the form [{"binsize": x, "id", y}]
  and groups them by binsize into an output object: {binsize: {binsize: x, id, y}}
  */
  var numberDatasets = data.length;
  var output = {};
  for (var index = 0; index < numberDatasets; index++) {
      var binsize = data[index]["binsize"];
      output[binsize] = {}
      output[binsize]["binsize"] = binsize
      output[binsize]["id"] = data[index]["id"]
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
