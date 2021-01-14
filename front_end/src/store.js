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
    datasets: null // datasets are in the global store because they will be shared for all functionalities for a given user throughout a session
  },
  getters: {
      isTokenEmpty: state => {
          return state.token == null
      },
      getCoolers: state => {
        return state.datasets.filter(
          (element) => element.filetype == "cooler" && (element.processing_state == "finished")
        );
      }
  },
  mutations: {
      setToken (state, tokenValue) {
        state.token = tokenValue
      },
      clearToken (state) {
        state.token = null
      },
      setDatasets (state, datasets) {
        state.datasets = datasets
      }
  }
})

export default store