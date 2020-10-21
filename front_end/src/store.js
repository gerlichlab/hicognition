import Vue from 'vue'
import Vuex from 'vuex'

// use store

Vue.use(Vuex)

// Define modules to separate state of tabs

const predefinedModule = {
  namespaced: true, // otherwise mutations are registered globally, this way mutations are available as "predefined/*"
  state: function() {
    return {
      pileupRegions: null,
      pileups: null,
      datasetSelection: null // This is the user's dataset selection for the predefined card
    }
  },
  mutations: {
      setPileupRegions (state, pileupRegions) {
        state.pileupRegions = pileupRegions
      },
      setPileups (state, pileups) {
        state.pileups = pileups
      },
      setDatasetSelection (state, selection) {
        state.datasetSelection = selection
      }
  }
}

// create global store

const store = new Vuex.Store({
  modules: {
    predefined: predefinedModule
  },
  state: {
    token: null,
    datasets: null // datasets are in the global store because they will be shared for all functionalities for a given user throughout a session
  },
  getters: {
      isTokenEmpty: state => {
          return state.token == null
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