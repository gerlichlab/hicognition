import Vue from 'vue'
import Vuex from 'vuex'

// use store

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    token: null,
    datasets: null,
    pileupRegions: null,
    pileups: null,
    datasetSelectionPredefined: null // This is the user's dataset selection for the predefined card
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
      },
      setPileupRegions (state, pileupRegions) {
        state.pileupRegions = pileupRegions
      },
      setPileups (state, pileups) {
        state.pileups = pileups
      },
      setDatasetSelectionPredefined (state, selection) {
        state.datasetSelectionPredefined = selection
      }
  }
})

export default store