import Vue from "vue";
import VueRouter from "vue-router";
import App from "./App";

Vue.config.productionTip = false;
Vue.config.errorHandler = function(err, vm, info) {
    /*
    This eats the select error from vue-matrial input select dropdowns
  */
    if (
        vm.$el.classList.contains("md-select") ||
        vm.$el.classList.contains("md-file")
    ) {
        return;
    }
    throw err;
};

import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "./themes/default.scss";
import store from "./store";
import Axios from "axios";

// add convenience methods for requests
Vue.prototype.$http = Axios;

// Vue.use specifies the use of a plugin, in this case VueMaterial
Vue.use(VueMaterial);

// use vue router
Vue.use(VueRouter);

// check whether token is available and set it if so

if (localStorage.getItem("hicognition-token")){
    store.commit("setToken", localStorage.getItem("hicognition-token"))
    store.commit("setUserId", localStorage.getItem("hicognition-User"))
}

// instantiate vue app

new Vue({
    el: "#app",
    store,
    components: {
        App
    },
    template: "<App/>"
});
