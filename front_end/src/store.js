import Vue from 'vue'
import Vuex from 'vuex'

// use store

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    token: null
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
      }
  }
})

export default store