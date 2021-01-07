import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'

Vue.config.productionTip = false

import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import './themes/default.scss'
import store from "./store"
import Axios from 'axios'



// add convenience methods for requests
Vue.prototype.$http = Axios;

// Vue.use specifies the use of a plugin, in this case VueMaterial
Vue.use(VueMaterial)

// use vue router
Vue.use(VueRouter)


new Vue({
  el: '#app',
  store,
  components: { 
    App
  },
  template: '<App/>'
})