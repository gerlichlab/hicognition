import Vue from 'vue'
import Vuex from 'vuex'

// use store

Vue.use(Vuex)

// Define modules to separate state of tabs

const predefinedModule = {
  namespaced: true, // otherwise mutations are registered globally, this way mutations are available as "predefined/*"
  state: function() {
    return {
      Intervals: null,
      averageIntervalData: null,
      individualIntervalData: null,
      datasetSelection: null // This is the user's dataset selection for the predefined card
    }
  },
  mutations: {
      setIntervals (state, Intervals) {
        state.Intervals = Intervals
      },
      setAverageIntervalData (state, averageIntervalData) {
        state.averageIntervalData = averageIntervalData
      },
      setIndividualIntervalData (state, individualIntervalData) {
        state.individualIntervalData = individualIntervalData
      },
      setDatasetSelection (state, selection) {
        state.datasetSelection = selection
      }
  }
}

const compareModule = {
  namespaced: true, // otherwise mutations are registered globally, this way mutations are available as "compare/*"
  state: function() {
    return {
      widgetCollections: {}, // collections of widgets that are currently displayed. Has structure {id: {children: {child_id: childProperties}}}
      widgetData: {} // data that is displayed by the widgets, is referenced by widgetCollections -> separate for performance reasons

    }
  },
  getters: {
      getWidgetProperties: (state) => (payload) => {
        return Object.assign({}, state.widgetCollections[payload.parentID]["children"][payload.id])
      },
      getCollectionProperties: (state) => (collectionID) => {
        return Object.assign({}, state.widgetCollections[collectionID])
      },
      collectionExists: (state) => (id) => {
        return id in state.widgetCollections
      },
      getCollectionConfig: (state) => (collectionID) => {
        if (!("collectionConfig") in state.widgetCollections[collectionID]){
          return {};
        }
        return Object.assign({}, state.widgetCollections[collectionID]["collectionConfig"]);
      },
      getWidgetDataPileup: (state) => (payload) => {
        if (!("pileup" in state.widgetData)){
          return undefined
        }
        return state.widgetData["pileup"][payload.pileupType][payload.id]
      },
      getWidgetDataStackup: (state) => (payload) => {
        if (!("stackup" in state.widgetData)){
          return undefined
        }
        return state.widgetData["stackup"][payload.stackupType][payload.id]
      },
      pileupExists: (state) => (payload) => {
        if (!("pileup" in state.widgetData)){
          return false;
        }
        return payload.id in state.widgetData["pileup"][payload.pileupType]
      },
      stackupExists: (state) => (payload) => {
        if (!("stackup" in state.widgetData)){
          return false;
        }
        return payload.id in state.widgetData["stackup"][payload.stackupType]
      },
      getWidgetType: (state) => (payload) => {
        if (payload.id in state.widgetCollections[payload.parentID]["children"]){
          return state.widgetCollections[payload.parentID]["children"][payload.id]["widgetType"]
        }
        return undefined;
      }
  },
  mutations: {
      clearWidgetCollections (state) {
        state.widgetCollections = {};
      },
      setWidgetCollection (state, payload) {
        // Vue.set is needed to preserve reactivity
        Vue.set(state.widgetCollections, payload.parentID, {children: {[payload.id]: payload}});
      },
      setCollectionConfig (state, payload){
        // This holds all the information that is specific to the collection and not the children
        Vue.set(state.widgetCollections[payload.id], "collectionConfig", payload.collectionConfig)
      },
      setWidget (state, payload) {
        // Vue.set is needed to preserve reactivity
        Vue.set(state.widgetCollections[payload.parentID]["children"], payload.id, payload);
      },
      deleteWidgetCollection (state, id) {
        // vue delete is needed to preserve reactivity
        Vue.delete(state.widgetCollections, id);
      },
      deleteWidget (state, payload) {
        // check whether widget exists before deletion
        if (payload.parentID in state.widgetCollections){
          // vue delete is needed to preserve reactivity
          Vue.delete(state.widgetCollections[payload.parentID]["children"], payload.id);
        }
      },
      setWidgetDataPileup (state, payload) {
        if (!("pileup" in state.widgetData)){
          // initialize pileup
          state.widgetData["pileup"] = {
            "ICCF": {},
            "ObsExp": {}
          }
        }
        state.widgetData["pileup"][payload.pileupType][payload.id] = payload.data
      },
      setWidgetDataStackup (state, payload) {
        if (!("stackup" in state.widgetData)){
          // initialize pileup
          state.widgetData["stackup"] = {
            "normal": {}
          }
        }
        state.widgetData["stackup"][payload.stackupType][payload.id] = payload.data
      },
      setWidgetType (state, payload) {
        Vue.set(state.widgetCollections[payload.parentID]["children"][payload.id], "widgetType", payload.widgetType);
      }
  }
}


// create global store

const store = new Vuex.Store({
  modules: {
    predefined: predefinedModule,
    compare: compareModule
  },
  state: {
    token: null,
    user_id: null,
    datasets: null // datasets are in the global store because they will be shared for all functionalities for a given user throughout a session
  },
  getters: {
      isTokenEmpty: state => {
          return state.token == null
      },
      getUserId: state => {
        return state.user_id
      },
      getCoolersDirty: state => {
        // gets cooler files that can be in the state of processing -> for compare view TODO: still needed?
        return state.datasets.filter(
          (element) => element.filetype == "cooler"
        );
      },
      getCoolers: state => {
        return state.datasets.filter(
          (element) => element.filetype == "cooler" && (element.processing_state == "finished")
        );
      },
      getBigwigs: state => {
        return state.datasets.filter(
          (element) => element.filetype == "bigwig" && (element.processing_state == "finished")
        );
      }
  },
  mutations: {
      setToken (state, tokenValue) {
        state.token = tokenValue
      },
      setUserId (state, id) {
        state.user_id = id
      },
      clearToken (state) {
        state.token = null
        state.user_id = null
      },
      setDatasets (state, datasets) {
        state.datasets = datasets
      }
  }
})

export default store