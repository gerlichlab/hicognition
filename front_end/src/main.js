import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'

Vue.config.productionTip = false
Vue.config.errorHandler = function(err, vm, info){
  /*
    This eats the select error from vue-matrial input select dropdowns
  */
  if (vm.$el.classList.contains("md-select")){
    return
  }
  throw err;
}

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