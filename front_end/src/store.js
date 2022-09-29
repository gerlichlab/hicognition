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
            used_datasets: new Map(), // ids of datasets used in this config with usage numbers
            used_collections: new Map(), // ids of collections used in this config with usage numbers
            request_pool: new Map() // map for requests that acts as semaphores for certain requests
        };
    },
    getters: {
        getWidgetCollections: state => {
            return state.widgetCollections;
        },
        getUsedDatasets: state => {
            return state.used_datasets;
        },
        getUsedCollections: state => {
            return state.used_collections;
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
        getWidgetDataLola: state => payload => {
            if (!("lola" in state.widgetData)) {
                return undefined;
            }
            return state.widgetData["lola"][payload.id];
        },
        getWidgetDataEmbedding1d: state => payload => {
            if (!("embedding1d" in state.widgetData)) {
                return undefined;
            }
            // check whether overlay index if present and get overlay in that case
            if ("overlayIndex" in payload) {
                return state.widgetData["embedding1d"][payload.id]["overlays"][
                    payload.overlayIndex
                ];
            }
            return state.widgetData["embedding1d"][payload.id]["points"];
        },
        getWidgetDataEmbedding2d: state => payload => {
            if (!("embedding2d" in state.widgetData)) {
                return undefined;
            }
            return state.widgetData["embedding2d"][payload.valueType][
                payload.id
            ];
        },
        widgetExists: state => payload => {
            // checks whether widget with id exists
            return (
                payload.id in
                state.widgetCollections[payload.parentID]["children"]
            );
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
            return payload.id in state.widgetData["stackup"];
        },
        associationDataExists: state => payload => {
            if (!("lola" in state.widgetData)) {
                return false;
            }
            return payload.id in state.widgetData["lola"];
        },
        embedding1dDataExists: state => payload => {
            if (!("embedding1d" in state.widgetData)) {
                return false;
            }
            // check first whether the request is for an overlayIndex or not
            if ("overlayIndex" in payload) {
                if (!(payload.id in state.widgetData["embedding1d"])) {
                    return false;
                }
                return (
                    payload.overlayIndex in
                    state.widgetData["embedding1d"][payload.id]["overlays"]
                );
            }
            return payload.id in state.widgetData["embedding1d"];
        },
        embedding2dDataExists: state => payload => {
            if (!("embedding2d" in state.widgetData)) {
                return false;
            }
            return (
                payload.id in state.widgetData["embedding2d"][payload.valueType]
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
        },
        getRequest: state => url => {
            if (!state.request_pool.has(url)) {
                return undefined;
            }
            return state.request_pool.get(url);
        }
    },
    mutations: {
        setRequest(state, payload) {
            state.request_pool.set(payload.url, payload.data);
        },
        clearAll(state) {
            (state.widgetCollections = {}),
                (state.used_datasets = new Map()),
                (state.used_collections = new Map()),
                (state.widgetData = {}),
                (state.request_pool = new Map());
        },
        decrement_usage_dataset(state, id) {
            if (state.used_datasets.has(id)) {
                var old_value = state.used_datasets.get(id);
                // decrement
                var new_value = (old_value -= 1);
                // delete is 0
                if (new_value == 0) {
                    state.used_datasets.delete(id);
                } else {
                    state.used_datasets.set(id, new_value);
                }
            }
        },
        decrement_usage_collections(state, id) {
            if (state.used_collections.has(id)) {
                var old_value = state.used_collections.get(id);
                // decrement
                var new_value = (old_value -= 1);
                // delete is 0
                if (new_value == 0) {
                    state.used_collections.delete(id);
                } else {
                    state.used_collections.set(id, new_value);
                }
            }
        },
        increment_usage_dataset(state, id) {
            if (state.used_datasets.has(id)) {
                var old_value = state.used_datasets.get(id);
                // decrement
                var new_value = (old_value += 1);
                state.used_datasets.set(id, new_value);
            } else {
                // initialize to one if not in there
                state.used_datasets.set(id, 1);
            }
        },
        increment_usage_collections(state, id) {
            if (state.used_collections.has(id)) {
                var old_value = state.used_collections.get(id);
                // decrement
                var new_value = (old_value += 1);
                state.used_collections.set(id, new_value);
            } else {
                // initialize to one if not in there
                state.used_collections.set(id, 1);
            }
        },
        setWidgetCollections(state, payload) {
            state.widgetCollections = payload;
        },
        clearWidgetCollections(state) {
            state.widgetCollections = {};
        },
        createEmptyWidgetCollection(state, id) {
            Vue.set(state.widgetCollections, id, {
                children: {}
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
            state.widgetData["stackup"][payload.id] = payload.data;
        },
        setWidgetDataLineprofile(state, payload) {
            if (!("lineprofile" in state.widgetData)) {
                // initialize pileup
                state.widgetData["lineprofile"] = [];
            }
            state.widgetData["lineprofile"][payload.id] = payload.data;
        },
        setWidgetDataLola(state, payload) {
            if (!("lola" in state.widgetData)) {
                // initialize data
                state.widgetData["lola"] = {};
            }
            state.widgetData["lola"][payload.id] = payload.data;
        },
        setWidgetDataEmbedding1d(state, payload) {
            if (!("embedding1d" in state.widgetData)) {
                // initialize data
                state.widgetData["embedding1d"] = {};
            }
            // check whether this is for overlayIndex or not
            if ("overlayIndex" in payload) {
                if (!(payload.id in state.widgetData["embedding1d"])) {
                    state.widgetData["embedding1d"][payload.id] = {
                        overlays: {},
                        points: undefined
                    };
                }
                state.widgetData["embedding1d"][payload.id]["overlays"][
                    payload.overlayIndex
                ] = payload.data;
            } else {
                if (payload.id in state.widgetData["embedding1d"]) {
                    state.widgetData["embedding1d"][payload.id]["points"] =
                        payload.data;
                } else {
                    state.widgetData["embedding1d"][payload.id] = {
                        overlays: {},
                        points: payload.data
                    };
                }
            }
        },
        setWidgetDataEmbedding2d(state, payload) {
            if (!("embedding2d" in state.widgetData)) {
                // initialize data
                state.widgetData["embedding2d"] = {
                    ICCF: {},
                    ObsExp: {}
                };
            }
            if (payload.id in state.widgetData["embedding2d"]) {
                state.widgetData["embedding2d"][payload.valueType][payload.id] =
                    payload.data;
            } else {
                state.widgetData["embedding2d"][payload.valueType][payload.id] =
                    payload.data;
            }
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

const COLORPALETTE = [
    "#AA8F66",
    "#ED9B40",
    "#2E5E61",
    "#BA3B46",
    "#823021",
    "#B58D17",
    "#125d98"
];

const store = new Vuex.Store({
    modules: {
        predefined: predefinedModule,
        compare: compareModule
    },
    state: {
        token: null,
        sessionToken: null,
        user_id: null,
        user_name: null,
        resolutions: null,
        datasetMetadataMapping: null,
        collections: null,
        datasets: null, // datasets are in the global store because they will be shared for all functionalities for a given user throughout a session
        usedSortOrders: Array(COLORPALETTE.length).fill(0), // flags for used numbers
        usedValueScales: Array(COLORPALETTE.length).fill(0),
        notificationSource: null,
        notifications: {
            read: [],
            new: []
        }
    },
    getters: {
        notificationSource: state => {
            return state.notificationSource;
        },
        getNextSortOrderColor: state => {
            let nextEmptyIndex = state.usedSortOrders.indexOf(0);
            if (nextEmptyIndex == -1) {
                return undefined;
            }
            var color = COLORPALETTE[nextEmptyIndex];
            return color;
        },
        getNextValueScaleColor: state => {
            let nextEmptyIndex = state.usedValueScales.indexOf(0);
            if (nextEmptyIndex == -1) {
                return undefined;
            }
            var color = COLORPALETTE[nextEmptyIndex];
            return color;
        },
        getResolutions: state => {
            return state.resolutions;
        },
        getDatasetMetadataMapping: state => {
            return state.datasetMetadataMapping;
        },
        isTokenEmpty: state => {
            return state.token == null;
        },
        sessionToken: state => {
            return state.sessionToken;
        },
        getUserId: state => {
            return state.user_id;
        },
        userName: state => {
            return state.user_name;
        },
        getDataset: state => id => {
            return state.datasets.filter(el => el.id === id)[0];
        },
        notifications: state => {
            return state.notifications.new.sort(
                (a, b) => new Date(b.time) - new Date(a.time)
            );
        }
    },
    mutations: {
        releaseNotificationSource(state) {
            state.notificationSource.close();
            state.notificationSource = null;
        },
        createNotificationSource(state) {
            state.notificationSource = new EventSource(
                process.env.NOTIFICATION_URL
            );
        },
        addNewNotification(state, notification) {
            state.notifications.new.push(notification);
        },
        setNotificationRead(state, id) {
            state.notifications.read.push(
                state.notifications.new.filter(el => el.id === id)
            );
            state.notifications.new = state.notifications.new.filter(
                el => el.id !== id
            );
        },
        clearNewNotifications(state, id) {
            state.notifications.read = state.notifications.read.concat(
                state.notifications.new
            );
            state.notifications.new = [];
        },
        setColorUsage(state, color) {
            let colorIndex = COLORPALETTE.indexOf(color);
            state.usedSortOrders = state.usedSortOrders.map((val, index) => {
                if (index == colorIndex) {
                    return 1;
                }
                return val;
            });
        },
        setValueScaleColorUsage(state, color) {
            let colorIndex = COLORPALETTE.indexOf(color);
            state.usedValueScales = state.usedValueScales.map((val, index) => {
                if (index == colorIndex) {
                    return 1;
                }
                return val;
            });
        },
        releaseColorUsage(state, color) {
            let colorIndex = COLORPALETTE.indexOf(color);
            state.usedSortOrders = state.usedSortOrders.map((val, index) => {
                if (index == colorIndex) {
                    return 0;
                }
                return val;
            });
        },
        releaseValueScaleColorUsage(state, color) {
            let colorIndex = COLORPALETTE.indexOf(color);
            state.usedValueScales = state.usedValueScales.map((val, index) => {
                if (index == colorIndex) {
                    return 0;
                }
                return val;
            });
        },
        setSessionToken(state, tokenValue) {
            state.sessionToken = tokenValue;
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
        setUserName(state, name) {
            state.user_name = name;
            localStorage.setItem("hicognition-UserName", name);
        },
        clearSessionToken(state) {
            state.sessionToken = null;
        },
        clearToken(state) {
            state.token = null;
            state.user_id = null;
            localStorage.removeItem("hicognition-token");
            localStorage.removeItem("hicognition-User");
            localStorage.removeItem("hicognition-UserName");
        },
        setDatasets(state, datasets) {
            state.datasets = datasets;
        },
        setCollections(state, collections) {
            state.collections = collections;
        },
        setResolutions(state, resolutions) {
            state.resolutions = resolutions;
        },
        setDatasetMetadataMapping(state, mapping) {
            state.datasetMetadataMapping = mapping;
        }
    }
});

export default store;
