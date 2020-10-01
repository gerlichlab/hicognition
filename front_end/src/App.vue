<template>
  <div class="page-container">
      <router-view></router-view>
  </div>
</template>

<script>
import drawer from "./components/drawer"
import toolbar from "./components/toolbar"
import VueRouter from 'vue-router'

// import routes

import mainRoute from "./routes/mainRoute"
import loginRoute from "./routes/loginRoute"
import predefinedRoute from "./routes/predefinedRoute"
import annotateRoute from "./routes/annotateRoute"
import exploreRoute from "./routes/exploreRoute"

// define routes

const routes = [
  { path: '/main', component: mainRoute,
    children : [{
      path: "predefined", component: predefinedRoute
      },
      {
      path: "explore", component: exploreRoute
      },
      {
      path: "annotate", component: annotateRoute
      }
      ]
    },
  { path: '/login', component: loginRoute }
]

var router = new VueRouter({routes})

export default {
  name: "mainApp",
  components: {
    drawer,
    toolbar
  },
  router
};
</script>

<style lang="scss" scoped>
.md-app {
  height: 100vh;
  border: 1px solid rgba(#000, 0.12);
}
</style>