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
        <div>
          <higlass></higlass>
          <pileupcard></pileupcard>
        </div>
      </md-app-content>

    </md-app>
  </div>
</template>

<script>
import pileupcard from "./components/pileupcard";
import higlass from "./components/higlass";
import drawer from "./components/drawer"
import toolbar from "./components/toolbar"

export default {
  name: "LastRowFixed",
  components: {
    pileupcard,
    higlass,
    drawer,
    toolbar
  },
  data: () => ({
    menuVisible: false,
  }),
};
</script>

<style lang="scss" scoped>
.md-app {
  max-height: 100vh;
  border: 1px solid rgba(#000, 0.12);
}
</style>