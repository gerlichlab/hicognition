<template>
  <div class="page-container">
    <md-app md-waterfall md-mode="fixed-last">

      <md-app-toolbar class="md-large md-dense md-primary">
        <toolbar @drawer-clicked="menuVisible = !menuVisible"></toolbar>
      </md-app-toolbar>

      <md-app-drawer :md-active.sync="menuVisible">
        <drawer></drawer>
      </md-app-drawer>

      <md-app-content>
        <router-view></router-view>
      </md-app-content>

    </md-app>
  </div>
</template>

<script>
import drawer from "./components/drawer"
import toolbar from "./components/toolbar"
import VueRouter from 'vue-router'

// import routes

import mainRoute from "./routes/mainRoute"
import loginRoute from "./routes/loginRoute"

// define routes

const routes = [
  { path: '/main', component: mainRoute },
  { path: '/login', component: loginRoute }
]

var router = new VueRouter({routes})

export default {
  name: "mainApp",
  components: {
    drawer,
    toolbar
  },
  data: () => ({
    menuVisible: false,
  }),
  router
};
</script>

<style lang="scss" scoped>
.md-app {
  height: 100vh;
  border: 1px solid rgba(#000, 0.12);
}
</style>