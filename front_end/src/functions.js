import { defaultConf, emptyConfLocal, bedPeView, coolerView, topView } from "./config_templates"


export function getDefaultViewConf() {
  // Returns default config file for Higlass using higlass.io as a source server
  return defaultConf
}

export function getEmptyConf() {
  // Returns empty config file for local Higlass server. URL is defined in config/dev.env.js
  return emptyConfLocal
}


export function constructViewConf(cooler, bed, bedPe) {
  /*
  Constructs a view configuration for Higlass from the passed
  cooler file and bedPe file (go to the center view)
  and the passed bed file (go to the top view).
  The datasets should be passed objects of this 
  shape: { "datasetName": name, "higlass_uuid": uuid, ... }
  */
  var returnConfig = JSON.parse(JSON.stringify(emptyConfLocal)); //deep copy; yes, this is the recommended way in js... https://www.javascripttutorial.net/object/3-ways-to-copy-objects-in-javascript/
  if (cooler) {
    var filledCooler = fillCooler(cooler);
    returnConfig["views"][0]["tracks"]["center"].push(filledCooler);
  }
  if (bed) {
    var filledBed = fillBed(bed);
    returnConfig["views"][0]["tracks"]["top"].push(filledBed);
  }
  if (bedPe) {
    var filledBedPe = fillBedPe(bedPe);
    returnConfig["views"][0]["tracks"]["center"].push(filledBedPe);
  }
  return returnConfig
}


function fillCooler(cooler) {
  // fills cooler file info into coolerView component
  // cooler should be an object like the following:
  // { "datasetName": name, "higlass_uuid": uuid, ...}
  var localView = JSON.parse(JSON.stringify(coolerView)); //deep copy; yes, this is the recommended way in js... https://www.javascripttutorial.net/object/3-ways-to-copy-objects-in-javascript/
  // assign uuid and name from cooler
  localView["contents"][0]["tilesetUid"] = cooler["higlass_uuid"];
  localView["contents"][0]["options"]["name"] = cooler["datasetName"];
  return localView;
}

function fillBedPe(bedPe) {
  // fills bedPe file info into bedPEView component
  // bedPe should be an object like the following:
  // { "datasetName": name, "higlass_uuid": uuid, ...}
  var localView = JSON.parse(JSON.stringify(bedPeView)); //deep copy; yes, this is the recommended way in js... https://www.javascripttutorial.net/object/3-ways-to-copy-objects-in-javascript/
  // assign uuid and name from cooler
  localView["tilesetUid"] = bedPe["higlass_uuid"];
  localView["options"]["name"] = bedPe["datasetName"];
  return localView;
}

function fillBed(bed) {
  // fills bed file info into topView component
  // bed should be an object like the following:
  // { "datasetName": name, "higlass_uuid": uuid, ...}
  var localView = JSON.parse(JSON.stringify(topView)); //deep copy; yes, this is the recommended way in js... https://www.javascripttutorial.net/object/3-ways-to-copy-objects-in-javascript/
  // assign uuid and name from cooler
  localView["tilesetUid"] = bed["higlass_uuid"];
  localView["options"]["name"] = bed["datasetName"];
  return localView;
}

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
  return [{
      src: {
      data: data,
      shape: [rowNumber, colNumber],
      dtype: "float32"
    }
  }
  ]
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
      newValue = jsonObject["value"][index];  // undefined * number is NaN
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
    console.log(data)
    var output = {};
    for (var index = 0; index < numberDatasets; index++) {
      var { id, binsize } = data[index];
      var value_type = "normal"
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



export function group_intervals_on_windowsize(intervals){
  /*
    data is array intervals object [{"id": 1, "windowsize": 20000, ...}]
    transform data from [{"id", "windowsize"}, ...] to {"windwosize: {"windowsize": 200000, id: [id1, id2,....]}, ...]
  */
  var output = {}
  for (var interval of intervals){
      var windowsize = interval.windowsize;
      if (windowsize in output){
          output[windowsize]["id"].push(interval.id);
      }
      else{
          output[windowsize] = {"windowsize": windowsize, "id": []};
          output[windowsize]["id"].push(interval.id);
      }
  }
  return output;
}

// Helpers for datasetTable

export function toLower(text) {
    return text.toString().toLowerCase()
  }

export function searchByName(items, term) {
  /*
  helper to search table fields by name for datasetTable
  */
    if (term) {
      var filtered_items = items.filter(item => {
          return toLower(item.dataset_name).includes(toLower(term))
          });
      return filtered_items
    }

    return items
  }