import Vue from "vue";
import Vuex from "vuex";

// use store

Vue.use(Vuex);

// Define modules to separate state of tabs

const predefinedModule = {
    namespaced: true, // otherwise mutations are registered globally, this way mutations are available as "predefined/*"
    state: function() {
        return {
            Intervals: null,
            averageIntervalData: null,
            individualIntervalData: null,
            datasetSelection: null // This is the user's dataset selection for the predefined card
        };
    },
    mutations: {
        setIntervals(state, Intervals) {
            state.Intervals = Intervals;
        },
        setAverageIntervalData(state, averageIntervalData) {
            state.averageIntervalData = averageIntervalData;
        },
        setIndividualIntervalData(state, individualIntervalData) {
            state.individualIntervalData = individualIntervalData;
        },
        setDatasetSelection(state, selection) {
            state.datasetSelection = selection;
        }
    }
};

const compareModule = {
    namespaced: true, // otherwise mutations are registered globally, this way mutations are available as "compare/*"
    state: function() {
        return {
            widgetCollections: {}, // collections of widgets that are currently displayed. Has structure {id: {children: {child_id: childProperties}}}
            widgetData: {}, // data that is displayed by the widgets, is referenced by widgetCollections -> separate for performance reasons
            used_datasets: new Map() // ids of datasets used in this config with usage numbers
        };
    },
    getters: {
        getWidgetCollections: state => {
            return state.widgetCollections
        },
        getUsedDatasets: state => {
            return state.used_datasets
        },
        getWidgetProperties: state => payload => {
            return Object.assign(
                {},
                state.widgetCollections[payload.parentID]["children"][
                    payload.id
                ]
            );
        },
        getCollectionProperties: state => collectionID => {
            return Object.assign({}, state.widgetCollections[collectionID]);
        },
        collectionExists: state => id => {
            return id in state.widgetCollections;
        },
        getCollectionConfig: state => collectionID => {
            if (!"collectionConfig" in state.widgetCollections[collectionID]) {
                return {};
            }
            return Object.assign(
                {},
                state.widgetCollections[collectionID]["collectionConfig"]
            );
        },
        getWidgetDataPileup: state => payload => {
            if (!("pileup" in state.widgetData)) {
                return undefined;
            }
            return state.widgetData["pileup"][payload.pileupType][payload.id];
        },
        getWidgetDataStackup: state => payload => {
            if (!("stackup" in state.widgetData)) {
                return undefined;
            }
            return state.widgetData["stackup"][payload.id];
        },
        getWidgetDataLineprofile: state => payload => {
            if (!("lineprofile" in state.widgetData)) {
                return undefined;
            }
            return state.widgetData["lineprofile"][payload.id];
        },
        widgetExists: state => payload => {
            // checks whether widget with id exists
            return payload.id in state.widgetCollections[payload.parentID]["children"]
        },
        pileupExists: state => payload => {
            if (!("pileup" in state.widgetData)) {
                return false;
            }
            return payload.id in state.widgetData["pileup"][payload.pileupType];
        },
        lineprofileExists: state => payload => {
            if (!("lineprofile" in state.widgetData)) {
                return false;
            }
            return payload.id in state.widgetData["lineprofile"];
        },
        stackupExists: state => payload => {
            if (!("stackup" in state.widgetData)) {
                return false;
            }
            return (
                payload.id in state.widgetData["stackup"]
            );
        },
        getWidgetType: state => payload => {
            if (
                payload.id in
                state.widgetCollections[payload.parentID]["children"]
            ) {
                return state.widgetCollections[payload.parentID]["children"][
                    payload.id
                ]["widgetType"];
            }
            return undefined;
        }
    },
    mutations: {
        clearAll(state){
          state.widgetCollections = {},
          state.used_datasets = new Map(),
          state.widgetData = {} 
        },
        decrement_usage_dataset(state, id){
            if (state.used_datasets.has(id)){
                var old_value = state.used_datasets.get(id)
                // decrement
                var new_value = old_value -=1
                // delete is 0
                if (new_value == 0){
                    state.used_datasets.delete(id)
                }else{
                    state.used_datasets.set(id, new_value)
                }
            } 
        },
        increment_usage_dataset(state, id){
            if (state.used_datasets.has(id)){
                var old_value = state.used_datasets.get(id)
                // decrement
                var new_value = old_value += 1
                state.used_datasets.set(id, new_value)
            }else{
                // initialize to one if not in there
                state.used_datasets.set(id, 1)
            }
        },
        setWidgetCollections(state, payload){
            state.widgetCollections = payload
        },
        clearWidgetCollections(state) {
            state.widgetCollections = {};
        },
        createEmptyWidgetCollection(state, id){
            Vue.set(state.widgetCollections, id, {
                children: { }
            });
        },
        setWidgetCollectionWithChild(state, payload) {
            // Vue.set is needed to preserve reactivity
            Vue.set(state.widgetCollections, payload.parentID, {
                children: { [payload.id]: payload }
            });
        },
        setCollectionConfig(state, payload) {
            // This holds all the information that is specific to the collection and not the children
            Vue.set(
                state.widgetCollections[payload.id],
                "collectionConfig",
                payload.collectionConfig
            );
        },
        setWidget(state, payload) {
            // Vue.set is needed to preserve reactivity
            Vue.set(
                state.widgetCollections[payload.parentID]["children"],
                payload.id,
                payload
            );
        },
        deleteWidgetCollection(state, id) {
            // vue delete is needed to preserve reactivity
            Vue.delete(state.widgetCollections, id);
        },
        deleteWidget(state, payload) {
            // check whether widget exists before deletion
            if (payload.parentID in state.widgetCollections) {
                // vue delete is needed to preserve reactivity
                Vue.delete(
                    state.widgetCollections[payload.parentID]["children"],
                    payload.id
                );
            }
        },
        setWidgetDataPileup(state, payload) {
            if (!("pileup" in state.widgetData)) {
                // initialize pileup
                state.widgetData["pileup"] = {
                    ICCF: {},
                    ObsExp: {}
                };
            }
            state.widgetData["pileup"][payload.pileupType][payload.id] =
                payload.data;
        },
        setWidgetDataStackup(state, payload) {
            if (!("stackup" in state.widgetData)) {
                // initialize pileup
                state.widgetData["stackup"] = {};
            }
            state.widgetData["stackup"][payload.id] =
                payload.data;
        },
        setWidgetDataLineprofile(state, payload) {
            if (!("lineprofile" in state.widgetData)) {
                // initialize pileup
                state.widgetData["lineprofile"] = [];
            }
            state.widgetData["lineprofile"][payload.id] =
                payload.data;
        },
        setWidgetType(state, payload) {
            Vue.set(
                state.widgetCollections[payload.parentID]["children"][
                    payload.id
                ],
                "widgetType",
                payload.widgetType
            );
        }
    }
};

// create global store

const COLORPALETTE = ["#AA8F66", "#ED9B40", "#2E5E61", "#BA3B46", "#823021", "#B58D17", "#125d98"]

const store = new Vuex.Store({
    modules: {
        predefined: predefinedModule,
        compare: compareModule
    },
    state: {
        token: null,
        sessionToken: null,
        user_id: null,
        resolutions: null,
        datasets: null, // datasets are in the global store because they will be shared for all functionalities for a given user throughout a session
        usedSortOrders: Array(COLORPALETTE.length).fill(0), // flags for used numbers
        usedValueScales: Array(COLORPALETTE.length).fill(0)
    },
    getters: {
        getNextSortOrderColor: state => {
            let nextEmptyIndex = state.usedSortOrders.indexOf(0)
            if (nextEmptyIndex == -1){
                return undefined
            }
            var color = COLORPALETTE[nextEmptyIndex]
            return color
        },
        getNextValueScaleColor: state => {
            let nextEmptyIndex = state.usedValueScales.indexOf(0)
            if (nextEmptyIndex == -1){
                return undefined
            }
            var color = COLORPALETTE[nextEmptyIndex]
            return color
        },
        getResolutions: state => {
            return state.resolutions
        },
        isTokenEmpty: state => {
            return state.token == null;
        },
        sessionToken: state => {
            return state.sessionToken
        },
        getUserId: state => {
            return state.user_id;
        },
        getCoolersDirty: state => {
            // gets cooler files that can be in the state of processing -> for compare view
            return state.datasets.filter(
                element => element.filetype == "cooler"
            );
        },
        getCoolers: state => {
            return state.datasets.filter(
                element =>
                    element.filetype == "cooler" &&
                    element.processing_state == "finished"
            );
        },
        getBigwigsDirty: state => {
            // gets bigwig files that can be in the state of processing -> for compare view
            return state.datasets.filter(
                element => element.filetype == "bigwig"
            );
        },
        getBigwigs: state => {
            return state.datasets.filter(
                element =>
                    element.filetype == "bigwig" &&
                    element.processing_state == "finished"
            );
        }
    },
    mutations: {
        setColorUsage(state, color){
            let colorIndex = COLORPALETTE.indexOf(color)
            state.usedSortOrders = state.usedSortOrders.map((val, index) => {
                if (index == colorIndex){
                    return 1
                }
                return val
            })
        },
        setValueScaleColorUsage(state, color){
            let colorIndex = COLORPALETTE.indexOf(color)
            state.usedValueScales = state.usedValueScales.map((val, index) => {
                if (index == colorIndex){
                    return 1
                }
                return val
            })
        },
        releaseColorUsage(state, color){
            let colorIndex = COLORPALETTE.indexOf(color)
            state.usedSortOrders = state.usedSortOrders.map((val, index) => {
                if (index == colorIndex){
                    return 0
                }
                return val
            })
        },
        releaseValueScaleColorUsage(state, color){
            let colorIndex = COLORPALETTE.indexOf(color)
            state.usedValueScales = state.usedValueScales.map((val, index) => {
                if (index == colorIndex){
                    return 0
                }
                return val
            })
        },
        setSessionToken(state, tokenValue){
            state.sessionToken = tokenValue
        },
        setToken(state, tokenValue) {
            state.token = tokenValue;
            // store token in local storage
            localStorage.setItem("hicognition-token", tokenValue);
        },
        setUserId(state, id) {
            state.user_id = id;
            localStorage.setItem("hicognition-User", id);
        },
        clearSessionToken(state){
            state.sessionToken = null
        },
        clearToken(state) {
            state.token = null;
            state.user_id = null;
            localStorage.removeItem("hicognition-token");
            localStorage.removeItem("hicognition-User");
        },
        setDatasets(state, datasets) {
            state.datasets = datasets;
        },
        setResolutions(state, resolutions){
            state.resolutions = resolutions
        }
    }
});

export default store;
