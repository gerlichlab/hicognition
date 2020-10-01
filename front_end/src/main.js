import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'

Vue.config.productionTip = false

import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

// Vue.use specifies the use of a plugin, in this case VueMaterial
Vue.use(VueMaterial)

// use vue router
Vue.use(VueRouter)


new Vue({
  el: '#app',
  components: { 
    App
  },
  template: '<App/>'
})

// instantiate higlass
/* const hgApi = hglib.viewer(
  document.getElementById('higlass-browser'),
  'http://higlass.io/api/v1/viewconfs/?d=default',
  {
    bounded: true,
    editable: false
  }
); */