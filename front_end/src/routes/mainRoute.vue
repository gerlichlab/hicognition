<template>

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
</template>>

<script>

import toolbar from "../components/toolbar";
import drawer from "../components/drawer";

export default {
name: "mainRoute",
  components: {
    toolbar,
    drawer
  },
  data: () => ({
    menuVisible: false,
  }),
}
</script>>